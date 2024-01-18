SELECT
	pi_inc.KEY_
	,bi.bi_id BI_ID --ID 
    ,pi.key_  --KI_NUMBER_FULL
    ,ti.name_ as TASKNAME --TASK_NAME
    ,(
          SELECT r.region_synonym
          FROM argus_sys.region_l r
          where r.parent_id=71203974
          connect by r.object_id = prior r.parent_id
          START WITH r.object_id = pi.regionid_
    ) FILIAL
    ,r.region_name as CITY -- REGION_NAME2
    ,r.region_tree_name --REGION_TREE_NAME
    ,ws.worksite_short_name --WORKSITE
    ,ti.assignee_name --ASSIGNEE_NAME
    ,coc.code_category_comment --CODE1			
    ,to_char(bi.open_date, 'dd.mm.yyyy hh24:mi:ss') as OPEN_DATE--OPEN_DATE
    ,to_char(ti.create_, 'dd.mm.yyyy hh24:mi:ss') as CREATE_KI--CREATE_KI
    ,to_char(ti.start_, 'dd.mm.yyyy hh24:mi:ss') as START_KI--START_KI --начало времени визита
    ,to_char(ti.finish_, 'dd.mm.yyyy hh24:mi:ss') as STOP_KI--STOP_KI --конец времени визита
    ,to_char(bi.CLOSE_DATE, 'dd.mm.yyyy hh24:mi:ss') as CLOSE_KI--STOP_KI --конец визита
    --,bi.is_repeated --IS_REPEATED
    --,(CASE WHEN (extract(minute from (ti.finish_- bi.open_date))/60+ extract(hour from (ti.finish_- bi.open_date))+ extract(day from (ti.finish_- bi.open_date))*24)<12 THEN 1 ELSE 0 END) AS KS_3
    ,(CASE WHEN bi.CLOSE_DATE IS NULL THEN (CASE WHEN (extract(minute from (ti.finish_- ti.create_))/60+ extract(hour from (ti.finish_- ti.create_))+ extract(day from (ti.finish_- ti.create_))*24)<12 THEN 1 ELSE 0 END) ELSE (CASE WHEN (extract(minute from (bi.CLOSE_DATE- ti.create_))/60+ extract(hour from (bi.CLOSE_DATE- ti.create_))+ extract(day from (bi.CLOSE_DATE- ti.create_))*24)<12 THEN 1 ELSE 0 END) end) AS KS_3
    ,(CASE WHEN (extract(minute from (bi.CLOSE_DATE-bi.open_date))/60+ extract(hour from (bi.CLOSE_DATE-bi.open_date))+ extract(day from (bi.CLOSE_DATE-bi.open_date))*24)<12 THEN 1 ELSE 0 END) AS KS_23
    ,(SELECT 
    listagg(t2.pi_key,' ')
    FROM argus_dwh."NP4_SCNI$3LTS_FACT" t2 
    JOIN argus_sys.BUSINESS_INTERACTION b 
    ON b.bi_id = t2.bi_id 
    WHERE b.client_id = bi.client_id
    AND t2.pi_key != pi_inc.KEY_ 
    AND t2.date_close >= ti.create_-30 
    AND t2.date_close <= ti.create_
	)  AS Pi_rep
	,to_char(CASE WHEN bi.CLOSE_DATE IS NULL THEN ti.finish_- bi.open_date ELSE bi.CLOSE_DATE-bi.open_date END, ' hh24:mi:ss') as ltp2_3
    ,to_char(CASE WHEN bi.CLOSE_DATE IS NULL THEN ti.finish_- ti.create_ ELSE bi.CLOSE_DATE-ti.create_ END, ' hh24:mi:ss') AS ltp3
    ,pi_inc.KEY_
    ,(SELECT 
    count(lg.class_) AS count_reopen 
    FROM JBPM.JBPM_LOG lg 
    JOIN JBPM.JBPM_TOKEN jt 
    ON lg.token_ = jt.id_ 
    JOIN argus_sys.BUSINESS_INTERACTION b 
    ON jt.processinstance_ = b.JBPM_PROCESSINSTANCE_ID 
    WHERE b.BI_ID = bi_inc.bi_id
    AND lg.message_ = 'Инцидент переоткрыт из Amdocs') + (CASE WHEN (SELECT listagg(t2.pi_key,' ') FROM argus_dwh."NP4_SCNI$3LTS_FACT" t2 JOIN argus_sys.BUSINESS_INTERACTION b ON b.bi_id = t2.bi_id WHERE b.client_id = bi.client_id AND t2.pi_key != pi_inc.KEY_ AND t2.date_close >= ti.create_-30 AND t2.date_close <= ti.create_) IS NULL THEN 0 ELSE 1 end ) AS REPEATED
    ,to_char(pi_inc.DUEDATE_, 'dd.mm.yyyy hh24:mi:ss') as DUEDATE--DUEDATE --КС
    ,bi.COMMENTARY --COMMENT
    ,lg.LOGIN
    ,wfm.DATE_CLOSE
    ,(CASE WHEN ((EXTRACT(day FROM (bi.open_date-wfm.DATE_CLOSE)))<=30) THEN 1 ELSE 0 END) as wfm30 
    -- ,gi.IMPACT_DEGREE, gi.NETWORK, gi.GPR_PROBLEM_NAME, gi.GRP_PROBLEM_ID
FROM jbpm.jbpm_taskinstance ti
    join jbpm.jbpm_processinstance pi
    on ti.procinst_ = pi.id_
    join argus_sys.business_interaction bi
    on pi.id_ = bi.jbpm_processinstance_id
    LEFT JOIN argus_dwh."NP4_SCNI$3LTS_FACT" t
    ON bi.bi_id =t.bi_id
    LEFT JOIN ARGUS_DWH.NP2_SCNI$WFM_ORDER_FACT wfm ON bi.SERVICE_ID = wfm.SERVICE_ID 
    join argus_sys.region_l r
    on pi.regionid_ = r.object_id
    left join ARGUS_SYS.CODE co
    on bi.code_id=co.code_id
    left join ARGUS_SYS.CODE_CATEGORY coc
    on co.code_category_id=coc.code_category_id
    left join ARGUS_SYS.SERVICE_L se
    on bi.service_id=se.object_id
    left join argus_sys.client cl
    on bi.client_id = cl.object_id
    left join ARGUS_SYS.WORKSITE ws
    on ti.pooledactorid_=ws.object_id
    left join ARGUS_SYS.WORKER_L wo
    on ti.ACTORID_=wo.object_id
    left join ARGUS_SYS.LOGIN_L lg
    on wo.OBJECT_ID=lg.WORKER_ID
    LEFT JOIN RT_GATE.GROUP_INTERACTIONS gi
    ON gi.GRP_PROBLEM_NUMBER = bi.TT_NUMBER
    LEFT JOIN ARGUS_SYS.BUSINESS_INTERACTION_WAIT biw ON biw.waited_bi_id = bi.bi_id
    LEFT JOIN ARGUS_SYS.BUSINESS_INTERACTION bi_inc ON bi_inc.bi_id = biw.waiting_bi_id
    LEFT JOIN jbpm.jbpm_processinstance pi_inc ON pi_inc.id_ = bi_inc.jbpm_processinstance_id
WHERE
      ti.name_ in ('3ЛТП.Линейный наряд','3ЛТП.Выездной наряд','Кросс.Решение проблемы','Автозал.Решение проблемы') AND r.ENTERPRISE_BRANCH_ID=1507
      and (
      to_char(ti.create_,'dd.mm.yyyy')= to_char(sysdate,'dd.mm.yyyy') OR
      ti.isopen_='1' )
      AND ti.ISCANCELLED_= 0
      --AND (WORKSITE_SHORT_NAME='Уч.СТПМС_1_Сургут' OR WORKSITE_SHORT_NAME='Уч.СТПМС_2_Сургут')
      AND (r.region_tree_name LIKE '%Нефтеюганск%' or r.region_tree_name LIKE '%Пыть%' or r.region_tree_name LIKE '%Пойк%' )