#!/usr/local/bin/python2.7

import parse_file
import process


MY_FILE = "newlinediabetesSBC.csv"

# Plan Limits
MAX_OOP = 500

# Plan Copays
RX_COPAY = 0
MEDICAL_COPAY = 0
DME_COPAY = 0
PREVENTIVE_COPAY = 0
OFFICE_COPAY = 20
LAB_COPAY = 0

# Plan Coinsurance
RX_COINSURANCE = .2
MEDICAL_COINSURANCE = .2
DME_COINSURANCE = 0
PREVENTIVE_COINSURANCE = 0
OFFICE_COINSURANCE = 0
LAB_COINSURANCE = 0

# Plan Deductibles
RX_DEDUCTIBLE = 0
MEDICAL_DEDUCTIBLE = 100
DME_DEDUCTIBLE = 0
PREVENTIVE_DEDUCTIBLE = 0
OFFICE_DEDUCTIBLE = 0
LAB_DEDUCTIBLE = 0

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
	copay_accum = 0

	# Start the application
	for line_item in new_data:

		# Rest values to zero for each claim
		plan_pay_total = 0
		member_pay_total = 0
		deductible_total = 0
		copay_total = 0
		benefit_copay = 0

		# Claim specific values
		allowed_amount = float(line_item["AmountAllowed"])
		category = line_item["Category"]
		bill_code = line_item["BillCode"]

		# Instantiate each class based on type of the claim
		office_visit = process.Adjudicate(allowed_amount)
		dme = process.Adjudicate(allowed_amount)
		rx = process.Adjudicate(allowed_amount)
		lab = process.Adjudicate(allowed_amount)
		vaccine = process.Adjudicate(allowed_amount)

		# Determine remaining amounts to reach plan maximums
		medical_deductible_remaining = (MEDICAL_DEDUCTIBLE - deductible_accum)
		max_oop_remaining = (MAX_OOP - member_pays_accum)

		def new_adjudicate():

			# Determines if the claim is excluded under the plan
			if bill_code == "OTC":
				claim.excluded()

			# Determines if the plan pays the claim at 100%
			if PLAN_PAYS_ALL:
				plan_fully_pays()

			# Pays claims at 100% after the OOP max is satisfied
			if claim.max_oop_met:
				claim.plan_fully_pays()

			# Assess plan specific deductible
			if not claim.medical_deductible_met and claim.amount:
				if allowed_amount <= medical_deductible_remaining:
					claim.full_deductible()
				elif allowed_amount > medical_deductible_remaining:
					claim.satisfy_deductible(medical_deductible_remaining)

			# Assess plan specific copay
			if not claim.max_oop_met and benefit_copay and claim.amount:
				if benefit_copay <= claim.amount:
					claim.full_copay(benefit_copay)
				elif benefit_copay > claim.amount:
					claim.partial_copay(benefit_copay)

			# Assess plan specific coinsurance
			if MEDICAL_COINSURANCE and claim.amount:
				claim.coinsurance(MEDICAL_COINSURANCE)
				if claim.member_pays > max_oop_remaining:
					claim.satisfy_oop(max_oop_remaining)

		if category == "Laboratory tests":
			claim = lab
			new_adjudicate()
			excluded_accum += lab.exclude
			plan_pays_accum += lab.plan_pays
			member_pays_accum += lab.member_pays
			deductible_accum += lab.deductible
			total_claim_accum += lab.claim_amount
			member_OOP_accum += lab.member_pays
			plan_pay_total = lab.plan_pays
			member_pay_total = lab.member_pays
			deductible_total = lab.deductible
			copay_total = lab.copay_amount
			copay_accum += lab.copay_amount

		if category == "Office visits & procedures":
			claim = office_visit
			benefit_copay = OFFICE_COPAY
			new_adjudicate()
			excluded_accum += office_visit.exclude
			plan_pays_accum += office_visit.plan_pays
			member_pays_accum += office_visit.member_pays
			deductible_accum += office_visit.deductible
			total_claim_accum += office_visit.claim_amount
			member_OOP_accum += office_visit.member_pays
			plan_pay_total = office_visit.plan_pays
			member_pay_total = office_visit.member_pays
			deductible_total = office_visit.deductible
			copay_total = office_visit.copay_amount
			copay_accum = office_visit.copay_amount

		if category == "Medical equipment and supplies":
			claim = dme
			new_adjudicate()
			excluded_accum += dme.exclude
			plan_pays_accum += dme.plan_pays
			member_pays_accum += dme.member_pays
			deductible_accum += dme.deductible
			total_claim_accum += dme.claim_amount
			member_OOP_accum += dme.member_pays
			plan_pay_total = dme.plan_pays
			member_pay_total = dme.member_pays
			deductible_total = dme.deductible
			copay_total = dme.copay_amount
			copay_accum = dme.copay_amount

		if category == "Pharmacy":
			claim = rx
			new_adjudicate()
			excluded_accum += rx.exclude
			plan_pays_accum += rx.plan_pays
			member_pays_accum += rx.member_pays
			deductible_accum += rx.deductible
			total_claim_accum += rx.claim_amount
			member_OOP_accum += rx.member_pays
			plan_pay_total = rx.plan_pays
			member_pay_total = rx.member_pays
			deductible_total = rx.deductible
			copay_total = rx.copay_amount
			copay_accum = rx.copay_amount

		if category == "Vaccines, other preventive":
			claim = vaccine
			new_adjudicate()
			excluded_accum += vaccine.exclude
			plan_pays_accum += vaccine.plan_pays
			member_pays_accum += vaccine.member_pays
			deductible_accum += vaccine.deductible
			total_claim_accum += vaccine.claim_amount
			member_OOP_accum += vaccine.member_pays
			plan_pay_total = vaccine.plan_pays
			member_pay_total = vaccine.member_pays
			deductible_total = vaccine.deductible
			copay_total = vaccine.copay_amount
			copay_accum = vaccine.copay_amount

		line_item["RunningClaimTotal"] = total_claim_accum
		line_item["PlanPay"] = plan_pay_total
		line_item["MemberPay"] = member_pay_total
		line_item["Deductible"] = deductible_total
		line_item["Copay"] = copay_total

		print 'Amount:', line_item["AmountAllowed"], '\t', 'Plan Pays:', line_item["PlanPay"], \
			  '\t', 'Member Pays:', line_item["MemberPay"], '\t', 'Copay Total:', line_item["Copay"], \
			  '\t', 'Deductible:', line_item["Deductible"], '\t', 'Running Deductible:', deductible_accum, \
			  '\t', 'Running OOP:', member_OOP_accum

	print "Total amount for all claims: %s" % total_claim_accum
	print "Member Paid: %s" % member_pays_accum
	print "Plan Paid: %s" % plan_pays_accum
	print "Deductible paid total: %s" % deductible_accum
	print "Total Excluded: %s" % excluded_accum


if __name__ == "__main__":
	main()