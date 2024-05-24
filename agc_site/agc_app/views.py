from django.db.models import Q
from django.db.models.functions import Coalesce
from django.shortcuts import *
from django.utils.datastructures import MultiValueDictKeyError

from .models import *


# .................................................................
# .................................................................
# ----------------- TODOs AND BUGs ------------------------------- #

# TODO: *******SETTINGS PAGE***********

# TODO: ****HUGE****: MANY MANY ACCOUNT TYPES, BUT 3 MAIN CATEGORIES OF ACCOUNTS:
#  1. CLIENT ACOUNT
#  2. CONTRACTOR TYPE (CARPENTAR, PAINTWORK, FULL-STACK-HOME, ETC ETC, CUSTOM (REQUIRES THEM TO MANUALLY MENTION ALL THEIR SERVICES)).
#  3. CORPORATE TYPE
#  THE CURRENT IMPLEMENTATION OF CONTRACTOR ACCOUNT MUST BE RENAMED TO CORPORATE TYPE,
#  WITH SERVICES RENAMED AS "PRODUCTS" AND "CONTACT BUTTON" REPLACED AS "BUY" BUTTON.
#  OTHER ACCOUNT TYPES CAN BUY FROM CORPORATE, AND ALL ITEMS BROUGHT WILL BE PUT IN A
#  SMALL REPORT. - IF A CONTRACTOR BUYS *AND* ADDS A NUMBER CORRESPONDING TO CLIENT'S PROJECT
#  DURING BUYING, THAN THAT SMALL REPORT WILL BE ADDED TO CLIENT'S PROJECT'S PAGE (IN BUY/SELL SECTION).
#  - AND -
#  DURING SIGNUP, THERE ARE 3 OPRIONS, CLIENT, CONTRACTOR, CORPORATE.
#  - AND -
#  FOR CONTRACTOR ACCOUNT, A SINGLE, LARGE (CONVERING FULL SCREEN) CARD WILL BE SHOWN WITH DETAILED INFO
#  WRITTEN BY THE COTRACTOR, HIS RATES, WORK, ETC, ETC. - ON CLICK, THIS CARD WILL ROTATE 180 AND A
#  FORM WITH DETAILS WILL APPEAR TO BE FILLED BY THE USER.
#  - AND -
#  ALL SERVICES (EXCEPT CUSTOM[MENTIONED ABOVE]) WILL BE PRE-DEFINED IN DATABASE, AND THEIR
#  ENTRY WILL BE PUT IN LIST-VIEW DIRING SIGNUP, AND IN SETTINGS. SELECTING MORE THAN 1 WILL
#  RESULT IN MORE CARDS ON THEIR PAGE. -- HOWEVER FOR CORPORATE, PAGE WILL BE SAME AS IT IS NOW.
#  - AND -
#  WHEN CLIENT FILLS THE FORM ONBACK OF A SERVICE AND CLICKS "PROCEED", THAN A SEPARATE PAGE
#  FOR REPORT WILL BE VREATED, WHERE THEY CAN NEGOTIATE AS WELL. THIS PAGE WILL TRACK ALL THE THINGS
#  HAPPENING TO THIS PROJECT (THE PROJECT CREATED IN DB WHEN CLIENT PROCEEDED.) each house/service-selection
#  will be a separate project with different page to contact bw contractor and client. -- however,
#  corporate account does not need to "contact/talk" to clinet because they are only for buying selling
#  purpose, so they dont need to talk. only report of what is brought from them.
#  :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#  :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

# BUG: IF 2 SERVICES OF SAME NAME ARE SAVED BY CONTRACTOR, THAN SELECTING ONE WILL SIMULTANEOUSLY
# SELECT OTHER AS WELL. THIS IS BECAUSE SERVICE'S NAME IS USED AS A SOLE WAY TO
# REFER TO SERVICE WHEN USER CLICKS 'ADD TO CART'.

# TODO: DISPLAY EMAIL, PHONE.NO.ETC TO CONTRACTOR DURING CONVO.

# TODO: *HUGE* MAKE CONVERSATIONS LIKE EMAIL, NOT LIKE CHAT. DISPLAY LIST OF ALL
#  MESSAGES ON CONVERSATIONS, ON-CLICK, DISPLAY THAT ENTIRE MESSAGE LIKE:
#  SUBJECT: TEXT: ...
#  SEND ADD TO CART REPORT AS AN EMAIL-LIKE MESSAGE, THEN SET IS_RECENT = FALSE or something
#   >>> STATUS: PENDING

# TODO: MAKE SEARCH FEATURE, BASED OF SEPARATE VIEW/TEMPLATE. TO SEARCH USERS BY USERNAME, NAME
#  AND FOR SEARCHING SERVICES. IT SHOULD SHOW feed/ LIKE PAGE SHOWING CARDS TELLING RATING OF
#  USER ALONG WITH ITS SERVICE (IF SEARCHED FOR SERVICE). ELSE SIMPLY PLACE CARDS OF USERS
#  LIKE IN feed/ PAGE. >>> STATUS: PENDING

# TODO: FILE UPLOADS HAVE NO MECHANISM TO CHECK WHETHER IT IS IMAGE FILE
#  OR ANY OTHER FILE. >>> STATUS: IGNORED

# .................................................................
# .................................................................

def index(request):
    template = loader.get_template('agc_app/index.html')
    context = { }

    try:
        me = get_object_or_404(User, username=request.session["username"])
        return HttpResponseRedirect('/user/' + me.username + '/')
    except KeyError:
        pass

    # login system:
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]

        try:
            user = User.objects.get(username=username)
            if password == user.password:
                request.session['username'] = user.username
                return HttpResponseRedirect('/user/' + username + '/')
            else:
                raise User.DoesNotExist
        except User.DoesNotExist:
            context = { 'login_error': True }

    return HttpResponse(template.render(context, request))


# .................................................................
# .................................................................

def signup(request):
    template = loader.get_template('agc_app/signup.html')
    context = { }

    # signup system:
    if request.method == 'POST':

        name = request.POST["name"]
        username = request.POST["username"]
        email = request.POST["email"]
        contact_number = request.POST["contact_number"]
        password = request.POST["password"]
        password_again = request.POST["password_again"]
        account_type = int(request.POST["account_type"])

        try:
            if User.objects.get(username=username):
                context = {'user_already_exists_error': True, }
                return HttpResponse(template.render(context, request))
        except User.DoesNotExist: pass

        if password == password_again:
            user = User()
            user.type = account_type
            user.name = name
            user.username = username
            user.email = email
            user.contact_number = contact_number
            user.password = password

            user.save()

            request.session['username'] = user.username
            return HttpResponseRedirect('/user/' + username + '/')

        else:
            context = {'password_not_matching_error': True, }

    return HttpResponse(template.render(context, request))


# .................................................................
# .................................................................


def userpage(request, username):
    template = loader.get_template('agc_app/userpage.html')
    context = {}

    try:
        me = get_object_or_404(User, username=request.session["username"])
    except KeyError:
        return HttpResponseRedirect('/')

    user = get_object_or_404(User, username=username)

    if request.method == 'POST':

        # add review+rating
        if 'add_review' in request.POST:
            if 'positive_review_button' in request.POST:
                is_positive = True # true=positive or false=negative
            else:
                is_positive = False
            review_text = request.POST["review_text"]

            review = Review.objects.filter(to_user=user).filter(by_user=me)
            if not review:
                review = Review()
                review.by_user = me
                review.to_user = user
            else: review = review[0]

            review.is_positive = is_positive
            review.text = review_text
            review.save()
            return HttpResponseRedirect('/user/' + user.username + '/')

        if 'update_offerings' in request.POST:
            offerings = request.POST['offerings']
            me.offerings = offerings
            me.save()
            return HttpResponseRedirect('/user/' + user.username + '/')

        # contact (after selecting service):
        if 'transaction' in request.POST:
            for_contract = get_object_or_404(Contract, pk=int(request.POST['contract_id']))

            text = request.POST['transaction_text']
            transaction = Transaction()
            transaction.by_user = me
            transaction.to_user = user
            transaction.for_contract = for_contract
            transaction.text = text
            transaction.save()
            products = Product.objects.filter(by_user=user)
            for product in products:
                if request.POST[str(product.pk)] == 'true': # if this service is selected by client
                    transaction.products.add(product)
            transaction.save()
            if (for_contract.to_user != me) and (for_contract.by_user != me):
                transaction.delete()
                context = { 'transaction_for_unknown_contract': True, } # BUG
                return HttpResponse(template.render(context, request))

        if 'add_product' in request.POST:
            new_product = Product()
            new_product.by_user = me
            new_product.name = request.POST["name"]
            new_product.text = request.POST["description"]
            new_product.price = request.POST["price"]
            new_product.photo = request.FILES["photo"]
            new_product.save()

        if 'delete_product' in request.POST:
            which_product = get_object_or_404(Product, pk=int(request.POST['delete_product']))
            which_product.delete()


        if 'edit_account_settings' in request.POST:
            name = request.POST["name"]
            email = request.POST["email"]
            contact_number = request.POST["contact_number"]
            password = request.POST["password"]
            password_again = request.POST["password_again"]
            account_type = int(request.POST["account_type"])

            me.type = account_type
            me.name = name
            me.email = email
            me.contact_number = contact_number
            try:
                profile_photo = request.FILES['profile_photo']
                me.photo = profile_photo
            except MultiValueDictKeyError: pass
            if password == password_again:
                me.password = password
                me.save()
                return HttpResponseRedirect('/user/' + user.username + '/')
            else:
                pass


    my_review = None
    try: my_review = Review.objects.filter(to_user=user, by_user=me)[0]
    except IndexError: pass

    context = {
        'user': user,
        'reviews': Review.objects.filter(to_user=user),

        'me': me,
        'my_review': my_review,
    }
    return HttpResponse(template.render(context, request))

# .................................................................
# .................................................................



def contracts_between(request, username):
    template = loader.get_template('agc_app/contracts.html')

    try:
        me = get_object_or_404(User, username=request.session["username"])
    except KeyError:
        return HttpResponseRedirect('/')

    user = get_object_or_404(User, username=username)

    # TODO: EXPECTED BUG?
    contracts = Contract.objects.filter(Q(to_user=me) | Q(by_user=user), Q(to_user=user) | Q(by_user=me))

    if request.method == 'POST':
        if 'create_new_contract' in request.POST:
            new_contract = Contract()
            new_contract.by_user = me
            new_contract.to_user = user
            new_contract.save()
            return HttpResponseRedirect('/contract/' + str(new_contract.pk) + '/')

    context = {
        'back_to_user': user,
        'me': me,
        'page': 'contracts_between',
        'contracts': contracts,
    }
    return HttpResponse(template.render(context, request))




def contracts_to_me(request):
    template = loader.get_template('agc_app/contracts.html')

    try:
        me = get_object_or_404(User, username=request.session["username"])
    except KeyError:
        return HttpResponseRedirect('/')

    contracts = Contract.objects.filter(to_user=me)

    context = {
        'back_to_user': me,
        'me': me,
        'page': 'contracts_to_me',
        'contracts': contracts,
    }

    return HttpResponse(template.render(context, request))




def contracts_by_me(request):
    template = loader.get_template('agc_app/contracts.html')

    try:
        me = get_object_or_404(User, username=request.session["username"])
    except KeyError:
        return HttpResponseRedirect('/')

    contracts = Contract.objects.filter(by_user=me)

    context = {
        'back_to_user': me,
        'me': me,
        'page': 'contracts_by_me',
        'contracts': contracts,
    }

    return HttpResponse(template.render(context, request))





# ACTUAL CONTRACT PAGE
def contract_page(request, pk):
    template = loader.get_template('agc_app/contract.html')

    contract = get_object_or_404(Contract, pk=pk)

    try:
        me = get_object_or_404(User, username=request.session["username"])
    except KeyError:
        return HttpResponseRedirect('/')

    user = get_object_or_404(User, username=contract.by_user.username)
    if user == me: user = get_object_or_404(User, username=contract.to_user.username)

    if request.method == 'POST':
        if 'contract_details_update' in request.POST:
            site_address = request.POST['site_address']
            description = request.POST['description']
            contract.site_address = site_address
            contract.description = description
            contract.save()
        if 'new_message' in request.POST:
            message = request.POST['message']
            msg = Message()
            msg.by_user = me
            msg.to_user = user
            msg.text = message
            msg.for_contract = contract
            msg.save()
        if 'create_transaction' in request.POST:
            transaction = Transaction()
            transaction.by_user = me
            transaction.to_user = me # to be re-written to the real corporate
            transaction.for_contract = contract
            transaction.save()
            return HttpResponseRedirect('/')#TODO:TO CORPORATES


    # TODO: DETAILS OF CONTRACT MUST BE IN CONTRACT CLASS (in progress)

    contract = get_object_or_404(Contract, pk=pk)
    transactions = Transaction.objects.filter(for_contract=contract)
    messages = Message.objects.filter(for_contract=contract)

    context = {
        'page': 'contract',
        'me': me,
        'contract': contract,
        'transactions': transactions,
        'messages': messages,
    }

    return HttpResponse(template.render(context, request))



def transactions_to_me(request):
    template = loader.get_template('agc_app/transactions.html')

    try:
        me = get_object_or_404(User, username=request.session["username"])
    except KeyError:
        return HttpResponseRedirect('/')

    transactions = Transaction.objects.filter(to_user=me)

    if request.method == 'POST':
        if 'confirm_transaction' in request.POST:
            which = get_object_or_404(Transaction, pk=int(request.POST['confirm_transaction']))
            which.is_confirmed = True
            which.save()

    context = {
        'back_to_user': me,
        'me': me,
        'page': 'transactions_to_me',
        'transactions': transactions,
    }

    return HttpResponse(template.render(context, request))


def reviews_page(request, username):
    template = loader.get_template('agc_app/reviews.html')

    try:
        me = get_object_or_404(User, username=request.session["username"])
    except KeyError:
        return HttpResponseRedirect('/')

    user = get_object_or_404(User, username=username)

    reviews = Review.objects.filter(to_user=user)

    context = {
        'back_to_user': user,
        'me': me,
        'user': user,
        'page': 'reviews_page',
        'reviews': reviews,
    }

    return HttpResponse(template.render(context, request))


# .................................................................
# .................................................................

def search(request):
    template = loader.get_template('agc_app/search.html')

    try:
        me = get_object_or_404(User, username=request.session["username"])
    except KeyError:
        me = None

    # process message and 'i have read' form
    if request.method == 'POST':
        if 'search' in request.POST:
            what = request.POST['search']

            users_by_name_filtered = User.objects.filter(name__contains=what, username__contains=what)
            users_by_offerings_filtered = User.objects.filter(offerings__contains=what)
            users_by_products_filtered = User.objects.filter(product_by_user_set__name__contains=what)
            context = {
                'me': me,
                'users_by_name_filtered': users_by_name_filtered,
                'users_by_offerings_filtered': users_by_offerings_filtered,
                'users_by_products_filtered': users_by_products_filtered,
            }
            return HttpResponse(template.render(context, request))

    # messages = Message.objects.filter(Q(to_user=user, by_user=me) | Q(to_user=me, by_user=user)).order_by('date')

    context = {'me': me,}

    return HttpResponse(template.render(context, request))


# .................................................................
# .................................................................

def settings(request):
    template = loader.get_template('agc_app/settings.html')

    try:
        me = get_object_or_404(User, username=request.session["username"])
    except KeyError:
        return HttpResponseRedirect('/')

    if request.method == 'POST':
        if 'update_info' in request.POST: # if update_info form is submitted

            new_profile_photo = None
            try: new_profile_photo = request.FILES["profile_photo"]
            except MultiValueDictKeyError: pass
            new_name = request.POST["name"]
            new_bio = request.POST["bio"]
            new_password = request.POST["password"]
            new_password_again = request.POST["password_again"]
            new_is_contractor = False
            try: new_is_contractor = request.POST["is_contractor"] == 'on'
            except MultiValueDictKeyError: pass
                # write new data from form to database
            if new_password == new_password_again:
                me.photo = new_profile_photo
                me.name = new_name
                me.bio = new_bio
                me.password = new_password
                me.is_contractor = new_is_contractor
                me.save()
            else:
                context = {'password_not_matching_error': True, }
                return HttpResponse(template.render(context, request))

    context = {
        'me': me,
    }

    return HttpResponse(template.render(context, request))


# .................................................................
# .................................................................

def home(request):
    template = loader.get_template('agc_app/home.html')

    try:
        me = get_object_or_404(User, username=request.session["username"])
    except KeyError:
        return HttpResponseRedirect('/')

    contractors = User.objects.filter(type=1) # .order_by('thumbs_up_by_user_set') will cause dupliate users bug.
    corporates = User.objects.filter(type=2) # .order_by('thumbs_up_by_user_set') will cause dupliate users bug.


    context = { # TODO: ADD SORTING BY THUMBS
        'me': me,
        'contractors': contractors,
        'corporates': corporates,
    }

    return HttpResponse(template.render(context, request))


# .................................................................
# .................................................................

def logout(request):
    template = loader.get_template('agc_app/logout.html')
    context = { }

    if request.method == 'GET':
        try:
            context = {'logged_out_user': request.session["username"], }
            if get_object_or_404(User, username=request.session["username"]):
                request.session.flush()
        except KeyError: pass

    return HttpResponse(template.render(context, request))

# .................................................................
# .................................................................

def about(request):
    template = loader.get_template('agc_app/about.html')
    context = { }
    return HttpResponse(template.render(context, request))