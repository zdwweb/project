# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.web
import dbconn
import web
import os
dbconn.register_dsn("host=localhost dbname=examdb user=examdbo password=pass")

settings = {
    "static_path": os.path.join('.', 'pages'),
    "debug": True
}


class BaseReqHandler(tornado.web.RequestHandler):

    def db_cursor(self, autocommit=True):
        return dbconn.SimpleDataCursor(autocommit=autocommit)
    
class MainHandler(BaseReqHandler):
    def get(self):
        self.set_header("Content-Type", "text/html; charSET=UTF-8")
        self.render(r"pages\base.html", title="首页")

class ScheduleHandler(BaseReqHandler):
    #显示排课信息
    def get(self):
        with self.db_cursor() as cur:
            sql = '''
                  SELECT tno,tname,cno,cname,week,time,classroom,object
                  FROM tc_schedule
                  ORDER BY tno,cno
                  '''
            cur.execute(sql)
            cur.commit()
            items = cur.fetchall()
        self.set_header("Content-Type", "text/html; charSET=UTF-8")
        self.render("pages\list.html", title="排课信息", items=items)


class CourseAddHandler(BaseReqHandler):
    #添加排课信息
    def post(self):
        try:
            week = int(self.get_argument("week"))
            time= int(self.get_argument("time"))
            cno = self.get_argument("cno")
            cname = self.get_argument("cname")
            classroom = self.get_argument("classroom")
            tname = self.get_argument("tname")
            tno = self.get_argument("tno")
            _cls = self.get_argument("class")
        except:
             self.redirect("/schedule")
        else:
            with self.db_cursor() as cur:
                sql_1 = '''SELECT cno,cname
                        FROM course
                        '''
                cur.execute(sql_1)
                c_list=cur.fetchall()
                sql_3 = '''SELECT tno,tname
                        FROM teacher
                        '''
                cur.execute(sql_3)
                t_list=cur.fetchall()
                sql_4 = '''SELECT classroom
                        FROM tc_schedule
                        WHERE week=%s AND time=%s
                        '''
                cur.execute(sql_4,(week,time))
                place_list=cur.fetchall()
                if (cno,cname) in c_list and (tno,tname) in t_list and (classroom,) not in place_list:
                    sql_2 = '''INSERT INTO tc_schedule
                           (week,time,cno,cname,classroom,tname,tno,object)
                           values
                           (%s,%s,%s,%s,%s,%s,%s,%s)'''
                    try:
                        cur.execute(sql_2, (week,time,cno,cname,classroom,tname,tno,_cls))
                        cur.commit()
                    except :
                        cur.rollback()
                    finally:
                        self.set_header("Content-Type", "text/html; charSET=UTF-8") 
                        self.redirect("/schedule")
                else:
                    if (cno,cname) not in c_list :
                        self.write(f"课程信息错误:课程号{cno} 课程名 {cname}")
                        return None
                    if (tno,tname) not in t_list:
                        self.write(f"教师信息错误:职工号{tno} 教师名 {tname}   ")
                        return None
                    if (classroom,)  in place_list:
                        self.write("教室冲突")
                        return None

class CourseDelHandler(BaseReqHandler):
    #删除排课信息
    def get(self, week,time,tno):
        week = int(week)
        time = int(time)
        
        with self.db_cursor() as cur:
            sql_1 = '''DELETE FROM tc_schedule
                       WHERE week=%s AND time=%s AND tno=%s 
            '''
            cur.execute(sql_1, (week,time,tno))
            cur.commit()
        self.set_header("Content-Type", "text/html; charSET=UTF-8")
        self.redirect("/schedule")

class CourseEditHandler(BaseReqHandler):
   #修改排课信息
    def get(self,week,time,tno):
        week = int(week)
        time = int(time)

        self.set_header("Content-Type", "text/html; charSET=UTF-8")
        with self.db_cursor() as cur:
            sql = '''
                SELECT cno,cname,classroom,object
                FROM tc_schedule
                WHERE week=%s AND time=%s AND tno=%s;
            '''
            cur.execute(sql,(week,time,tno))
            cur.commit()
            row = cur.fetchone()
            if row:
                self.render("pages\edit.html", week=week,time=time,tno=tno,
                 cno=row[0],cname=row[1],classroom=row[2],object=row[3])
            else:
                self.write('Not FOUND!')
    
    def post(self,week,time,tno):
        week = int(week)
        time = int(time)
        cno = self.get_argument("cno")
        cname = self.get_argument("cname")
        classroom = self.get_argument("classroom")
        _cls = self.get_argument("class")
        self.set_header("Content-Type", "text/html; charSET=UTF-8")
        with self.db_cursor() as cur:
            sql_2 = '''SELECT cno,cname
                        FROM course
            '''
            cur.execute(sql_2)
            c_list=cur.fetchall()
            sql_3 = '''SELECT classroom
                        FROM tc_schedule
                        WHERE week=%s AND time=%s AND tno!=%s
            '''
            cur.execute(sql_3,(week,time,tno))
            place_list=cur.fetchall()
            sql_1 = '''UPDATE tc_schedule SET 
                      cno=%s,cname=%s,
                      classroom=%s,object=%s
                      WHERE week=%s AND time=%s AND tno=%s
                      
                '''
            cur.execute(sql_1, (cno,cname,classroom,_cls,week,time,tno))
            cur.commit()
            if (cno,cname) not in c_list  :
                self.write(f"课程信息错误:课程号{cno}  课程名 {cname} ")
                cur.rollback()
            elif (classroom,)  in place_list:
                self.write("教室冲突")
                cur.rollback()
            else:
                self.redirect("/schedule")
        
class StudentCourseHandler(BaseReqHandler):
    #学生课程表
    def post(self):
        _cls = self.get_argument("_cls")
        with self.db_cursor() as cur:
            cur.execute('''UPDATE s_chart  as a SET
                           cname= b.cname,classroom=b.classroom,tname=b.tname
                           FROM tc_schedule as b
                           WHERE a.week= b.week AND a.time= b.time AND b.object=%s
            ''',(_cls,))
            cur.commit()
        self.redirect("/student_course")
                
    def get(self):
        course=[]
        with self.db_cursor() as cur:
             for i in range(1,5):
                 cur.execute('''SELECT cname,classroom,tname
                               FROM s_chart
                               WHERE time=%s 
                               ORDER BY week''',(i,))
                 cur.commit()
                 course.append(list(cur.fetchall()))
        self.render("pages\s_chart.html", first=course[0],second=course[1],
                    third=course[2],fourth=course[3])


class TeacherCourseHandler(BaseReqHandler):
   #教师课程表
    def post(self):
        teacher = self.get_argument("teacher")
        with self.db_cursor() as cur:
            cur.execute('''UPDATE t_chart  as a SET
                           cname= b.cname,classroom= b.classroom,object=b.object
                           FROM tc_schedule as b
                           WHERE a.week= b.week AND a.time=b.time AND b.tname=%s
            ''',(teacher,))
            cur.commit()
        self.redirect("/teacher_course")
    def get(self):
        course=[]
        with self.db_cursor() as cur:
            
            for i in range(1,5):
                cur.execute('''SELECT cname,classroom,object
                               FROM t_chart
                               WHERE time=%s 
                               ORDER BY week''',(i,))
                cur.commit()
                course.append(list(cur.fetchall()))
        self.render(r"pages\t_chart.html", first=course[0],second=course[1],
                    third=course[2],fourth=course[3])

class TCourseClearHandler(BaseReqHandler):
    #清空教师课程表
    def get(self):
        with self.db_cursor() as cur:
            cur.execute("""UPDATE  t_chart SET
                           cname=null,classroom=null,object=null
            """)
            cur.commit()
        self.redirect("/teacher_course")

class SCourseClearHandler(BaseReqHandler):
    #清空学生课程表
    def get(self):
        with self.db_cursor() as cur:
            cur.execute("""UPDATE  s_chart SET
                           cname=null,classroom=null,tname=null
            """)
            cur.commit()
        self.redirect("/student_course")


class CoursesListHandler(BaseReqHandler):
    def get(self):
        with self.db_cursor() as cur:
            cur.execute('''SELECT * FROM course  ORDER BY cno''')
            cur.commit()
            items = cur.fetchall()
        self.render(r"pages\s_list.html", title="课程清单",items=items)

class TeachersListHandler(BaseReqHandler):
    def get(self):
        with self.db_cursor() as cur:
            cur.execute('''SELECT * FROM teacher ORDER BY tno''')
            cur.commit()
            items = cur.fetchall()
        self.render(r"pages\t_list.html", title="教师清单",items=items)

application= tornado.web.Application([
    (r"/", MainHandler),
    (r"/schedule", ScheduleHandler),
    (r"/course.add",CourseAddHandler),
    (r"/course.del/([0-9]+)/([0-9]+)/([0-9]+)",CourseDelHandler),
    (r"/course.edit/([0-9]+)/([0-9]+)/([0-9]+)",CourseEditHandler),
    (r"/student_course", StudentCourseHandler),
    (r"/teacher_course", TeacherCourseHandler),
    (r"/tcourse.clear", TCourseClearHandler),
    (r"/scourse.clear", SCourseClearHandler),
    (r"/teachers",TeachersListHandler),
    (r"/courses", CoursesListHandler),
    (r'/(.*)', web.HtplHandler)
], **settings)


if __name__ == "__main__":
    application.listen(8888)
    server = tornado.ioloop.IOLoop.instance()
    tornado.ioloop.PeriodicCallback(lambda: None, 500, server).start()
    server.start()

