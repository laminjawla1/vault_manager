from .models import Withdraw, Deposit
from datetime import datetime

def get_opening_and_additional(deposits):
    op, ad = 0, 0
    for deposit in deposits:
        if deposit.approved and deposit.zone:
            if deposit.date.strftime('%Y-%m-%d') != datetime.utcnow().strftime('%Y-%m-%d'):
                return op, ad
            if deposit.deposit_type == "Opening Cash":
                op += deposit.amount
            else:
                ad += deposit.amount
    return op, ad

def get_todays_withdrawals():
    w, a = 0, 0
    for withdrawal in Withdraw.query.order_by(Withdraw.date.desc()).all():
        if withdrawal.approved:
            if withdrawal.date.strftime('%Y-%m-%d') != datetime.utcnow().strftime('%Y-%m-%d'):
                return w, a
            if withdrawal.date.strftime('%Y-%m-%d') == datetime.utcnow().strftime('%Y-%m-%d'):
                w += 1
                a += withdrawal.amount
    return w, a

def get_todays_deposits():
    d, a = 0, 0
    for deposit in Deposit.query.order_by(Deposit.date.desc()).all():
        if deposit.date.strftime('%Y-%m-%d') == datetime.utcnow().strftime('%Y-%m-%d'):
            if deposit.zone and deposit.approved:
                d += 1
                a += deposit.amount
        else:
            return d, a
    return d, a

def gmd(value):
    """Format value as GMD"""
    if not "GMD" in str(value):
        return f"GMD {value:,.2f}"
    return value