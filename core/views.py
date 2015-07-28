from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F
from django.views.generic import CreateView, TemplateView, ListView, DetailView
from django.views.generic.edit import UpdateView
from .models import Person, Entry, Proposal, Contract, Customer, Work, Employee, NumLastProposal, Category
from .forms import PersonForm, CustomerForm, StatusSearchForm
from .lists import status_list
from django.http import HttpResponseRedirect


def home(request):
    return render(request, 'index.html')


def status(request):
    return render(request, 'status.html')


class LoginRequiredMixin(object):

    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class CounterMixin(object):

    def get_context_data(self, **kwargs):
        context = super(CounterMixin, self).get_context_data(**kwargs)
        context['count'] = self.get_queryset().count()
        return context


class FirstnameSearchMixin(object):

    def get_queryset(self):
        queryset = super(FirstnameSearchMixin, self).get_queryset()
        q = self.request.GET.get('search_box')
        if q:
            return queryset.filter(
                Q(first_name__icontains=q) |
                Q(company__icontains=q))
        return queryset


class PersonList(CounterMixin, FirstnameSearchMixin, ListView):
    template_name = 'core/person/person_list.html'
    model = Person
    paginate_by = 10


class PersonDetail(DetailView):
    template_name = 'core/person/person_detail.html'
    model = Person


class PersonCreate(LoginRequiredMixin, CreateView):
    template_name = 'core/person/person_form.html'
    form_class = PersonForm
    success_url = reverse_lazy('person_list')


class PersonUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'core/person/person_form.html'
    model = Person
    form_class = PersonForm
    success_url = reverse_lazy('person_list')


class EntryList(CounterMixin, ListView):
    template_name = 'core/entry/entry_list.html'
    model = Entry
    context_object_name = 'entrys'
    paginate_by = 10

    def get_queryset(self):
        e = Entry.objects.filter(is_entry=False).select_related()
        q = self.request.GET.get('search_box')
        if q is not None:
            e = e.filter(
                Q(work__name_work__icontains=q) |
                Q(work__customer__first_name__icontains=q))
        return e


class EntryDetail(DetailView):
    template_name = 'core/entry/entry_detail.html'
    model = Entry
'''
    def get_object(self):
        pk = super(EntryDetail, self).get_object()
        employee = Employee.objects.get(pk=1)  # TODO
        nlp = NumLastProposal.objects.get(pk=1)  # sempre pk=1
        entry = Entry.objects.get(pk=self.kwargs['pk'])
        obj = Proposal(
            num_prop=nlp.num_last_prop + 1,
            type_prop='R',
            category=entry.category,
            description=entry.description,
            work=entry.work,
            person=entry.person,
            employee=employee,
            seller=entry.seller,
        )
        obj.save()

        entry.is_entry = True
        entry.save()

        nlp.num_last_prop += 1
        nlp.save()

        return obj
'''


class EntryActionMixin(object):

    @property
    def action(self):
        msg = "{0} is missing action.".format(self.__class__)
        raise NotImplementedError(msg)

    def form_valid(self, form):
        msg = "Entrada {0}!".format(self.action)
        messages.info(self.request, msg)
        return super(EntryActionMixin, self).form_valid(form)


class EntryCreate(LoginRequiredMixin, CreateView, EntryActionMixin):
    template_name = 'core/entry/entry_form.html'
    model = Entry
    fields = '__all__'
    success_url = reverse_lazy('entry_list')
    action = 'criada'


class EntryUpdate(LoginRequiredMixin, UpdateView,  EntryActionMixin):
    template_name = 'core/entry/entry_form.html'
    model = Entry
    fields = '__all__'
    success_url = reverse_lazy('entry_list')
    action = 'atualizada'


class ProposalList(CounterMixin, ListView):
    template_name = 'core/proposal/proposal_list.html'
    model = Proposal
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(ProposalList, self).get_context_data(**kwargs)
        context.update({'status_search_form': StatusSearchForm(), })
        context['status'] = status_list
        return context

    def get_queryset(self):
        p = Proposal.objects.select_related().all()

        if 'c' in self.request.GET:
            return p.filter(status__exact='c')
        if 'elab' in self.request.GET:
            return p.filter(status__exact='elab')
        if 'p' in self.request.GET:
            return p.filter(status__exact='p')
        if 'co' in self.request.GET:
            return p.filter(status__exact='co')
        if 'a' in self.request.GET:
            return p.filter(status__exact='a')
        # acho que da pra melhorar esses if usando
        # <li name="{{ item }}"><a href="?status={{ item }}">{{ item }}</a></li>
        # no template

        q = self.request.GET.get('search_box')
        # s = self.request.GET.get('status')
        if q is not None:
            # try:
            p = p.filter(
                Q(id__icontains=q) |
                Q(work__name_work__icontains=q) |
                Q(work__customer__first_name__icontains=q) |
                Q(category__category__startswith=q) |
                Q(employee__user__first_name__startswith=q) |
                Q(seller__employee__user__first_name__startswith=q))
            # Q(created__year=q))
            # except ValueError:
            #     pass
        # if s:
            # p = p.filter(status__exact=s)
        return p


class ProposalDetail(DetailView):
    template_name = 'core/proposal/proposal_detail.html'
    model = Proposal


class ProposalUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'core/proposal/proposal_form.html'
    model = Proposal
    fields = '__all__'
    success_url = reverse_lazy('proposal_list')


class ContractList(CounterMixin, ListView):
    template_name = 'core/contract/contract_list.html'
    model = Contract
    paginate_by = 10


class ContractDetail(DetailView):
    template_name = 'core/contract/contract_detail.html'
    model = Contract


class ContractUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'core/contract/contract_form.html'
    model = Contract
    fields = '__all__'
    success_url = reverse_lazy('contract_list')


class CustomerList(CounterMixin, FirstnameSearchMixin, ListView):
    template_name = 'core/customer/customer_list.html'
    model = Customer
    paginate_by = 10


class CustomerDetail(DetailView):
    template_name = 'core/customer/customer_detail.html'
    model = Customer


class CustomerCreate(LoginRequiredMixin, CreateView):
    template_name = 'core/customer/customer_form.html'
    form_class = CustomerForm
    success_url = reverse_lazy('customer_list')


class CustomerUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'core/customer/customer_form.html'
    model = Customer
    form_class = CustomerForm
    success_url = reverse_lazy('customer_list')


class WorkList(CounterMixin, ListView):
    template_name = 'core/work/work_list.html'
    model = Work
    paginate_by = 10

    def get_queryset(self):
        w = Work.objects.all().select_related()
        q = self.request.GET.get('search_box')
        if q is not None:
            w = w.filter(
                Q(name_work__icontains=q) |
                Q(customer__first_name__icontains=q))
        return w


class WorkDetail(DetailView):
    template_name = 'core/work/work_detail.html'
    model = Work


class WorkCreate(LoginRequiredMixin, CreateView):
    template_name = 'core/work/work_form.html'
    model = Work
    fields = '__all__'
    success_url = reverse_lazy('work_list')


class WorkUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'core/work/work_form.html'
    model = Work
    fields = '__all__'
    success_url = reverse_lazy('work_list')