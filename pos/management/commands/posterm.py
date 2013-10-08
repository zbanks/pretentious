from django.core.management.base import BaseCommand, CommandError
from pos.models import *
from datetime import datetime, timedelta
from django.db.models import Avg, Max, Sum, Count
import decimal
import sys

D = decimal.Decimal

WAITING = 1
CUSTOMER = 2
CREDIT = 3
PRODUCT = 4
RETAB = 5
NEWTAB = 6

SPECIAL_CMDS = {"quit", "cash", "new", "product", "!retab", "!cancel", "!undo", "!fridge"}

TIMEOUT = 60


class Command(BaseCommand):
    args = ''
    help = 'Runs the Point-of-Sale interface'

    def handle(self, *args, **kwargs):
        state = WAITING
        last_transaction = None
        customer = None

        def out(x, raw=False):
            if not raw:
                self.stdout.write('   ' + x)
            else:
                self.stdout.write(x, ending='')
        
        def inp():
            val = sys.stdin.readline()
            logcmd = InputLog.objects.create(text=val, customer=customer)
            return val.strip().lower(), logcmd

        bug = sys.stderr.write
        last_time = datetime.now()
        newlines = 0

        while True:
            # Block and read input
            if state == WAITING:
                out(" > ", raw=True)
            elif state == CREDIT:
                out("  $", raw=True)
            else:
                out(" : ", raw=True)
            command, logcmd = inp()

            # Log input

            if not command:
                # Blank newline, ignore
                if newlines >= 5 and newlines % 5 == 0:
                    # Clear screen & timeout
                    state = WAITING
                    customer = None
                    #XXX clear
                newlines += 1
                continue
            newlines = 0

            # Look up the SHA1 hash of the command. Don't need to keep barcodes in the DB
            sha1cmd = hashlib.sha1(command).hexdigest()

            # Deal with timeouts
            time = datetime.now()
            if (time - last_time).total_seconds() > TIMEOUT:
                last_time = time
                if state != WAITING:
                    out("Your action was timed out. Don't take so long!")
                last_transaction = None
                customer = None
                state = WAITING
                continue
            last_time = time

            if state == CREDIT:
                try:
                    amount = D(command.strip("$"))
                except decimal.InvalidOperation:
                    out("Invalid amount. Enter the number of dollars you're adding to your tab.")
                assert customer
                if abs(amount) > 200:
                    # Probably a mistake
                    out("That's a lot. I'm assuming that was a mistake. The most you can credit at once is $200")
                else:
                    transaction = Transaction.objects.create(customer=customer, credit=amount)
                    last_transaction = transaction
                    if amount > 30:
                        out("Cool. Put ${:0.2f} in the cashbox or venmo @zbanks. Try to pay off your tab faster next time :(".format(amount))
                    elif amount < -10:
                        out("Cool. Take ${:0.2f} from the cashbox. That seems like a lot though. Are you sure?".format(amount))
                    elif amount > 0:
                        out("Cool. Put ${:0.2f} in the cashbox now. (Alternatively venmo @zbanks)".format(amount))
                    elif amount < 0:
                        out("Cool. Take ${:0.2f} from the cashbox now. ".format(amount))
                    else:
                        out("Uhh, okay... *shrug* whatever.")
                    out("Scan 'Undo' if there was a mistake or you need to change the amount.")
                customer = None
                state = WAITING
                continue
            elif state == NEWTAB:
                if Barcode.objects.filter(sha1text=sha1cmd).exists():
                    out("That's already been taken. Try another name (e.g. your athena or favorite 4-letter word)")
                elif command in SPECIAL_CMDS:
                    out("Nice try. That's a reserved word. Way to be an asshole.")
                elif User.objects.filter(username=command).exists():
                    out("That's weird. I think that name is already taken? Anyways, try another name.")
                    bug("Name already taken, but not a customer: `{}`".format(command))
                else:
                    customer = Customer.objects.create(
                        user=User.objects.create_user(username=command),
                        require_password=False,
                        is_trusted=True
                    )
                    barcode = Barcode.objects.create(
                        customer=customer,
                        text=command,
                        is_active=True
                    )
                    out("Awesome. Thanks for setting up a tab!")
                    out("To buy a drink, type/scan your tab name, then scan your drink")
                    out("To add (or remove) cash from your tab, scan the 'Cash' barcode and follow the prompts.")
                    out("You should try to keep a positive balance, and *only* record cash deposits when you physically put in cash.")
                    out("Bug zbanks (zbanks@mit.edu) with any questions or bugs.")
                    out("If you forget any of this, or want to learn more, scan the 'HELP!' barcode to get help.")
                    out("")
                    out("Welcome to Pretentious!")
                    state = WAITING
                    customer = None
                    continue

            # Some commands are hardcoded & aren't barcodes
            if command in SPECIAL_CMDS:
                logcmd.special_match = True
                logcmd.save()

                if command == "quit":
                    break
                elif command == "cash":
                    if state != CUSTOMER or not customer:
                        out("First enter your tab name (or scan your tab barcode), then scan the 'Cash' barcode afterwards.")
                        continue
                    state = CREDIT
                    out("How much cash are you adding to your tab?")
                elif command == "new":
                    state = NEWTAB
                    out("Hello new user! Let's set up a tab.")
                    out("What should the tab be named? (Probably your name, athena, or something else you can remember)")
                elif command == "!fridge":
                    for product in Product.objects.all():
                        store = product.stocking_set.filter(in_machine=False).aggregate(Sum('cost'), Sum('quantity'))
                        machine = product.stocking_set.filter(in_machine=True).aggregate(Sum('cost'), Sum('quantity'))
                        trans = product.transaction_set.filter(void=False).aggregate(Sum('credit'), Count('pk'))

                        out("> {0.name} (${0.price:0.2f}) (active={0.is_active})".format(product))
                        out(" - Expense: ${0:0.2f} ({1}); Revenue: ${2:0.2f} ({3}); In machine: ${4:0.2f} ({5})".format(
                                store["cost__sum"] or 0, store["quantity__sum"] or 0,
                                trans["credit__sum"] or 0, trans["pk__count"] or 0,
                                (machine["cost__sum"] or 0) - (trans["credit__sum"] or 0),
                                (machine["quantity__sum"] or 0)- (trans["pk__count"] or 0)))
                elif command == "product":
#state = PRODUCT
                    if not customer or not customer.user.username == "zach":
                        out("lol no")
                        continue
                    while True:
                        out("Change Product; Scan code")
                        # This is special, so we'll handle this oddly
                        code, __ = inp()
                        if code in {'', "q", "quit", "!cancel", "cancel", "quit"}:
                            break
                        bcs = Barcode.objects.filter(text=code)
                        if bcs.exists():
                            barcode = bcs.get()
                            out("Looks like the barcode is in the system.")
                            if not barcode.is_active:
                                out("It's inactive, but whatever.")
                            if barcode.customer:
                                out("It's a customer. lawl.")
                                continue
                            elif barcode.product:
                                product = barcode.product
                            else:
                                out("That barcode is weird. You should fix it in admin")
                                continue
                        else:
                            barcode = Barcode.objects.create(text=code)
                            out("This looks like a new product. Name?")
                            p_name, __ = inp()
                            if not p_name:
                                out("Nevermind then.")
                            out("Price")
                            price = D(inp()[0].strip('$'))
                            product = Product.objects.create(
                                    name=p_name,
                                    slug=p_name,
                                    price=price,
                                    description=p_name,
                                    shortcut=code,
                                    ordering=0,
                                    is_active=True)
                            barcode.product = product
                            barcode.save()
                            out("Made product.")
                        out("How many were purchased?")
                        try:
                            num = int(inp()[0])
                        except:
                            out("Nevermind")
                            continue
                        if num > 0:
                            out("For how much (total)")
                            amt = D(inp()[0])
                            Stocking.objects.create(
                                user=customer,
                                product=product,
                                quantity=num,
                                in_machine=False,
                                cost=amt)
                            out("Stocked")
                        out("How many did you add to the machine")
                        try:
                            num = int(inp()[0])
                        except:
                            out("Nevermind")
                            continue
                        Stocking.objects.create(
                            user=customer,
                            product=product,
                            quantity=num,
                            in_machine=True)
                        out("Stocked into machine")
                elif command == "!retab":
                    state = WAITING
                    if last_transaction:
                        last_transaction.void = True
                        new_t = Transaction.objects.create(
                                customer=customer,
                                product=last_transaction.product,
                                credit=last_transaction.credit
                                )
                        last_transaction = new_t
                        out("Changed tab for last transaction")
                    else:
                        out("No transaction to change")
                elif command == "!undo":
                    if state == WAITING:
                        if last_transaction:
                            last_transaction.void = not last_transaction.void
                            last_transaction.save()
                            if last_transaction.void:
                                out("Voided last transaction")
                            else:
                                out("Unvoided last transaction")
                        else:
                            out("No transaction to void")
                    else:
                        out("Cancelled.")
                        state = WAITING
                        customer = None
                elif command == "!cancel":
                    out("Cancelled.")
                    state = WAITING
                    customer = None
                else:
                    out("Oops, that seems like a bug. I'm going to report that.")
                    bug("Bug: unknown special command `{}`".format(command))
                continue

            try:
                barcode = Barcode.objects.filter(sha1text=sha1cmd).get()
            except Barcode.DoesNotExist:
                # The barcode isn't known
                out("That's a weird barcode. Try scanning it again.")
                continue
            except Barcode.MultipleObjectsReturned:
                # That's awkward...
                barcode = Barcode.objects.filter(text=command)[0]
                bug("Looking up barcode `{}` resulted in mutliple objects".format(command))

            logcmd.barcode_match = True
            logcmd.save()

            if barcode.product:
                product = barcode.product
                if state == WAITING:
                    trans = Transaction.objects.create(customer=None, product=product, credit=-product.price)
                    out("You just bought a {} (${:0.2f}) with cash.".format(product.name, product.price))
                    out("Scan 'Oops -- Put on Tab' and then your tab's barcode to put it on your tab instead.")
                    out("Scan 'Oops -- Undo' if this isn't correct.")
                    last_transaction = trans
                elif state == CUSTOMER:
                    trans = Transaction.objects.create(customer=customer, product=product, credit=-product.price)
                    out("You just bought a {} (${:0.2f}) on tab.".format(product.name, product.price))
                    out("You have ${:0.2f} left to spend on your tab".format(customer.balance))
                    out("Scan 'Oops -- Undo' if this was a mistake.")
                    last_transaction = trans
                    state = WAITING
                    customer = None

            elif barcode.customer:
                customer = barcode.customer
                if state in {WAITING, CUSTOMER, CREDIT}:
                    if customer.balance < 5:
                        out("Hello again! You currently have a tab of -${:0.2f}. You should pay it off soon.".format(abs(customer.balance)))
                    elif customer.balance > 0:
                        out("Hello! You have ${:0.2f} left on your tab".format(customer.balance))
                    else:
                        out("Hello! You have a tab of -${:0.2f}. (You can still buy drinks though)".format(abs(customer.balance)))
                    out("Scan a drink to buy it on your tab")
                    out("Scan 'Credit' to add money to your tab")
                    out("Scan 'Cancel' to do nothing or buy on cash.")
                    state = CUSTOMER
                elif state == PRODUCT:
                    out("That didn't make sense.")
                    state = WAITING
                    customer = None

