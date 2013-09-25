#!/usr/local/bin/python2.7

import parse_file
import process

MY_FILE = "newlinediabetesSBC.csv"

# Plan Limits
MAX_OOP = 500
RX_COPAY = 0
MEDICAL_COPAY = 0
RX_COINSURANCE = .2
MEDICAL_COINSURANCE = .2
RX_DEDUCTIBLE = 0
MEDICAL_DEDUCTIBLE = 100
PLAN_PAYS_ALL = False


def main():
    # Call our parse function and give it the needed parameters
    new_data = parse_file.parse(MY_FILE, ",")

    # Set the Accumulator List
    deductible_accum = 0
    member_OOP_accum = 0
    total_claim_accum = 0
    excluded_accum = 0
    plan_pays_accum = 0
    member_pays_accum = 0

    # Start the application
    for line_item in new_data:
        allowed_amount = float(line_item["AmountAllowed"])
        bill_code = line_item["BillCode"]
        claim = process.Adjudicate(allowed_amount)
        medical_deductible_remaining = (MEDICAL_DEDUCTIBLE - deductible_accum)
        max_oop_remaining = (MAX_OOP - member_pays_accum)
        
        if bill_code == "OTC":
            claim.excluded()

        if PLAN_PAYS_ALL:
        	plan_fully_pays()
        
        if claim.max_oop_met:
            claim.plan_fully_pays()
        
        if not claim.medical_deductible_met and claim.amount:
            if allowed_amount <= medical_deductible_remaining:
                claim.full_deductible()
            elif allowed_amount > medical_deductible_remaining:
                claim.satisfy_deductible(medical_deductible_remaining)

        if MEDICAL_COINSURANCE and claim.amount:
            claim.coinsurance(MEDICAL_COINSURANCE)
            if claim.member_pays > max_oop_remaining:
            	claim.satisfy_oop(max_oop_remaining)

        if MEDICAL_COPAY and claim.amount:
        	claim.copay(MEDICAL_COPAY)


        excluded_accum += claim.exclude
        plan_pays_accum += claim.plan_pays
        member_pays_accum += claim.member_pays
        deductible_accum += claim.deductible
        total_claim_accum += claim.claim_amount
        member_OOP_accum += claim.member_pays
        line_item["RunningClaimTotal"] = total_claim_accum  
        line_item["PlanPay"] = claim.plan_pays
        line_item["MemberPay"] = claim.member_pays
        line_item["Deductible"] = claim.deductible
        print 'Amount:', line_item["AmountAllowed"], '\t', 'Plan Pays:', line_item["PlanPay"], \
              '\t', 'Member Pays:', line_item["MemberPay"], '\t', 'Deductible:', \
              line_item["Deductible"], '\t', 'Running Deductible:', deductible_accum, \
              '\t' 'Running OOP:', member_OOP_accum


    print "Total amount for all claims: %s" % total_claim_accum
    print "Member Paid: %s" % member_pays_accum
    print "Plan Paid: %s" % plan_pays_accum
    print "Deductible paid total: %s" % deductible_accum
    print "Total Excluded: %s" % excluded_accum


if __name__ == "__main__":
    main()