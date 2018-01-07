DROP DATABASE IF EXISTS examdb;


DROP ROLE IF EXISTS examdb;
 

-- 创建一个登陆角色（用户），用户名examdbo, 缺省密码pass

CREATE ROLE examdbo LOGIN
  ENCRYPTED PASSWORD 'md568cefad35fed037c318b1e44cc3480cf' -- password: pass
  NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE;


CREATE DATABASE examdb WITH OWNER = examdbo ENCODING = 'UTF8';
   

