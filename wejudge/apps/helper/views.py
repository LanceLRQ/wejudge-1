from django.shortcuts import render

# Create your views here.

import wejudge.kernel.helper as Helper


def index(request):
    view_body = Helper.Helper(request)
    view_body.index()
    return view_body.render()


def guide_student(request):
    view_body = Helper.Helper(request)
    view_body.StudentGuide()
    return view_body.render()


def guide_student_viewer(request, vindex):
    view_body = Helper.Helper(request)
    view_body.StudentGuideViewer(int(vindex))
    return view_body.render()