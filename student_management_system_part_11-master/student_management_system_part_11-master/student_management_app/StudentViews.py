import datetime

from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

from student_management_app.models import Students, Courses, Subjects, CustomUser, Attendance, CourseCount,\
     NotificationStudent


def student_home(request):
    student_obj=Students.objects.get(admin=request.user.id)
    attendance_total=Attendance.objects.filter(student_id=student_obj).count()
    attendance_present=Attendance.objects.filter(student_id=student_obj,status=True).count()
    attendance_absent=Attendance.objects.filter(student_id=student_obj,status=False).count()
    course=Courses.objects.get(id=student_obj.course_id.id)
    subjects=Subjects.objects.filter(course_id=course).count()
    subjects_data=Subjects.objects.filter(course_id=course)
    
    
    return render(request,"student_template/student_home_template.html",{"total_attendance":attendance_total,"attendance_absent":attendance_absent,"attendance_present":attendance_present,"subjects":subjects})



def student_view_attendance(request):
    student=Students.objects.get(admin=request.user.id)
    course=student.course_id
    subjects=Subjects.objects.filter(course_id=course)
    return render(request,"student_template/student_view_attendance.html",{"subjects":subjects})

def student_view_attendance_post(request):
    subject_id=request.POST.get("subject")
      
    student=Students.objects.get(admin=request.user.id)
    attendance = Attendance.objects.filter(student_id=student.id, subject_id=subject_id)

    # attendance=Attendance.objects.filter(attendance_date__range=(start_data_parse,end_data_parse),subject_id=subject_obj)
    # attendance_reports=AttendanceReport.objects.filter(attendance_id__in=attendance,student_id=stud_obj)
    return render(request,"student_template/student_attendance_data.html", {"attendance_reports":attendance})

def student_mark_attendance(request):
    student=Students.objects.get(admin=request.user.id)
    course=student.course_id
    subjects=Subjects.objects.filter(course_id=course)
    return render(request,"student_template/student_mark_attendance.html",{"subjects":subjects})

def student_mark_attendance_check_course(request):
    student=Students.objects.get(admin=request.user.id)
    subject_id=request.POST.get("subject")
    is_lecture = CourseCount.objects.get(subject_id=subject_id)
    lecture_date = is_lecture.updated_at
    if lecture_date == datetime.date(datetime.now()):
        attendance = Attendance.objects.filter(student_id=student.id, subject_id=subject_id, status=False, attendance_date=datetime.date(datetime.now()))
        if attendance:
            Attendance.objects.filter(student_id=student.id, subject_id=subject_id, attendance_date=datetime.date(datetime.now())).update(status= True)
            attendance = Attendance.objects.filter(student_id=student.id, subject_id=subject_id)
            return render(request,"student_template/student_attendance_data.html", {"attendance_reports":attendance})
        else:
            return render(request, "student_template/student_attendance_already_marked.html")
    return render(request, "student_template/student_no_lecture.html")


def student_profile(request):
    user=CustomUser.objects.get(id=request.user.id)
    student=Students.objects.get(admin=user)
    return render(request,"student_template/student_profile.html",{"user":user,"student":student})

def student_profile_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("student_profile"))
    else:
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        password=request.POST.get("password")
        address=request.POST.get("address")
        try:
            customuser=CustomUser.objects.get(id=request.user.id)
            customuser.first_name=first_name
            customuser.last_name=last_name
            if password!=None and password!="":
                customuser.set_password(password)
            customuser.save()

            student=Students.objects.get(admin=customuser)
            student.address=address
            student.save()
            messages.success(request, "Successfully Updated Profile")
            return HttpResponseRedirect(reverse("student_profile"))
        except:
            messages.error(request, "Failed to Update Profile")
            return HttpResponseRedirect(reverse("student_profile"))

@csrf_exempt
def student_fcmtoken_save(request):
    token=request.POST.get("token")
    try:
        student=Students.objects.get(admin=request.user.id)
        student.fcm_token=token
        student.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

def student_all_notification(request):
    student=Students.objects.get(admin=request.user.id)
    notifications=NotificationStudent.objects.filter(student_id=student.id)
    return render(request,"student_template/all_notification.html",{"notifications":notifications})

