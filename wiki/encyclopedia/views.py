from django.shortcuts import render ,redirect
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
from . import util
from django.http import HttpResponse
import markdown2
from django.views import defaults


class SearchForm(forms.Form):
    search_query = forms.CharField(label="")

class NewForm(forms.Form):
    new_title = forms.CharField(label="Enter the title of the new page", widget=forms.TextInput(attrs={'placeholder': 'Title', 'style': 'width: 300px;', 'class': 'form-control'}))
    new_body = forms.CharField(label="Enter the markdown body of the new page", widget=forms.Textarea(attrs={'placeholder': 'Body', 'class': 'form-control'}))

class EditForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}))
    body = forms.CharField(label="Edit the markdown body of the page", widget=forms.Textarea(attrs={'class': 'form-control'}))


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": SearchForm()
    })


def entry(request, title="entry"):
    if util.get_entrt_try_all(title):
        return render(request, "encyclopedia/entry.html", {
            "entry": markdown2.markdown(util.get_entrt_try_all(title)),
            "title" : title,
            "form": SearchForm(),
            "entries": util.list_entries(),
            "entry_flag": True
        })
    else:
        return render(request, "encyclopedia/entry.html", {
            "title" : title,
            "form": SearchForm(),
            "entries": util.list_entries(),
            "entry_flag": False
        })


def new(request):
    if request.method == "POST":
        form = NewForm(request.POST)
        if form.is_valid():
            new_title = form.cleaned_data["new_title"]
            new_body = form.cleaned_data["new_body"]
            if util.get_entrt_try_all(new_title):
                return render(request, "encyclopedia/new.html", {
                    "form": SearchForm(),
                    "entries": util.list_entries(),
                    "new_form": form,
                    "error_msg": "ERROR : This title already exists"
                })
            else:
                util.save_entry(new_title, new_body)
                return redirect("encyclopedia:entry", title=new_title)
        else:
            return render(request, "encyclopedia/new.html", {
                "form": SearchForm(),
                "entries": util.list_entries(),
                "new_form": form,
            })
    else:
        return render(request, "encyclopedia/new.html", {
        "form": SearchForm(),
        "entries": util.list_entries(),
        "new_form": NewForm()
    })


def search(request):
    form = SearchForm(request.POST)
    if form.is_valid():
        title = form.cleaned_data["search_query"]
        if util.get_entrt_try_all(title):
            return HttpResponseRedirect(reverse("encyclopedia:entry", args=[title]))
        else:
            list_all_entries = util.list_entries()
            list_valid_entries = list(filter(lambda x: title.lower() in x.lower(), list_all_entries))
            return render(request, "encyclopedia/search.html", {
            "title": title,
            "valid_entries": list_valid_entries,
            "entries": util.list_entries(),
            "form": SearchForm()
            })
    else:
        return render(request,"encyclopedia/search.html", {
            "entries": util.list_entries(),
            "form": form
        })



def edit(request, title):
    if request.method == "POST":
        form = EditForm(request.POST)
        if form.is_valid():
            body = form.cleaned_data["body"]
            title = form.cleaned_data["title"]
            util.save_entry(title, body)
            return redirect("encyclopedia:entry", title=title)
        else:
            return render(request, "encyclopedia/edit.html", {
                "form": SearchForm(),
                "entries": util.list_entries(),
                "edit_form": form,
            })
    else:
        if util.get_entrt_try_all(title):
            body = util.get_entrt_try_all(title)
            return render(request, "encyclopedia/edit.html", {
                "title" : title,
                "form": SearchForm(),
                "entries": util.list_entries(),
                "edit_form": EditForm(initial = {"title": title, "body": body})
            })
        else:
            return defaults.page_not_found(request, "")

