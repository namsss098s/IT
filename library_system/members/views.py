from django.shortcuts import render, redirect, get_object_or_404
from .models import Member
from .forms import MemberForm


def member_list(request):
    members = Member.objects.all()
    return render(request, 'members/member_list.html', {'members': members})


def member_create(request):
    form = MemberForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('member_list')

    return render(request, 'members/member_form.html', {'form': form})


def member_update(request, pk):
    member = get_object_or_404(Member, pk=pk)
    form = MemberForm(request.POST or None, instance=member)

    if form.is_valid():
        form.save()
        return redirect('member_list')

    return render(request, 'members/member_form.html', {'form': form})


def member_delete(request, pk):
    member = get_object_or_404(Member, pk=pk)
    member.delete()
    return redirect('member_list')