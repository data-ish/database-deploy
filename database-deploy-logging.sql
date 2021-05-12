CREATE SCHEMA IF NOT EXISTS dbdeploy;


/* Simple lookup table */
CREATE TABLE IF NOT EXISTS dbdeploy.activitytype(
    activitytypeid smallint primary key,
    activitytype varchar(32)
);


WITH activity_types as (
    select 1 as activitytypeid, 'START' as activitytype
    union all select 2, 'SUCCESS'
    union all select 3, 'FAILURE'
)
INSERT INTO dbdeploy.activitytype(activitytypeid, activitytype)
SELECT activitytypeid, activitytype 
FROM activity_types as t 
WHERE NOT EXISTS (select activitytypeid from dbdeploy.activitytype as d WHERE t.activitytypeid = d.activitytypeid)
;


/* For deployments that are not repeatable keep track of success and failure here */
CREATE TABLE IF NOT EXISTS dbdeploy.activity(
    activityid serial primary key,
    activitytimestamp timestamptz default now(),
    filename varchar(256),
    activitytypeid smallint,
    CONSTRAINT FK_activitytypeid foreign key (activitytypeid) references dbdeploy.activitytype(activitytypeid)
);


/* For deployments that are not repeatable keep track of what has been successfully deployed here */
CREATE TABLE IF NOT EXISTS dbdeploy.deployed(
    deployedid serial primary key,
    filename varchar(256),
    deployedtimestamp timestamptz default now()
);