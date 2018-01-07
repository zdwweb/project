--课程总表
CREATE TABLE course
(
    cno text  NOT NULL,--课程号
    cname text ,--课程名
    PRIMARY KEY (cno)
)
--教师总表
CREATE TABLE teacher                                                                                               CREATE TABLE teacher
(
    tno text  NOT NULL,--职工号
    tname text ,--教师名
    PRIMARY KEY (tno)
)
--排课信息表
CREATE TABLE tc_schedule
(
    tno text  NOT NULL,--职工号
    tname text ,--教师名
    cno text,--课程号
    cname text ,--课程名
    classroom text,--教室
    object text ,--授课对象
    week integer NOT NULL,--星期
    time integer NOT NULL,--节次
    PRIMARY KEY (tno, week, time)
)
--学生课程表
CREATE TABLE s_chart
(
    week integer NOT NULL,
    time integer NOT NULL,
    cname text ,
    tname text ,
    classroom text ,
    CONSTRAINT  PRIMARY KEY (week, time)
)

--教师课程表
CREATE TABLE t_chart
(
    week integer NOT NULL,
    time integer NOT NULL,
    cno text ,
    cname text,
    classroom text,
    tname text,
    tno text,
    object text,
    PRIMARY KEY (week, time)
)

       




  