class Adjudicate:
    max_oop_met = False
    medical_deductible_met = False
    rx_deductible_met = False
    plan_pays = 0
    member_pays = 0
    exclude = 0
    deductible = 0

    
    def __init__(self, amount):
        self.claim_amount = amount
        self.amount = amount
    
    # Claim is excluded in plan language and member pays 100%
    def excluded(self):
        self.exclude = self.amount
        self.amount -= self.exclude
    
    # Member has satisfied plan max OOP and plan pays 100%
    def plan_fully_pays(self):
        self.plan_pays = self.amount
        self.amount -= self.plan_pays

    # Assess copay to the claim
    def copay(self, copay):
        self.copay = copay
        self.member_pays = self.copay
        self.amount -= self.copay

    # Assess coinsurance to the claim
    def coinsurance(self, coinsur):
        self.coinsur = coinsur
        self.member_pays += self.amount * self.coinsur
        self.plan_pays = self.amount * (1 - self.coinsur)
    
    # Assess deductible to the claim
    def full_deductible(self):
        self.deductible = self.amount
        self.amount -= self.amount
        
    # Satisfy deductible and prepare for further adjudication
    def satisfy_deductible(self, remaining_deductible):
        self.remaining_deductible = remaining_deductible
        self.deductible = self.remaining_deductible
        self.amount -= self.deductible
        self.medical_deductible_met = True
    
    def satisfy_oop(self, remaining_oop):
        self.remaining_oop = remaining_oop
        self.over_oop = self.member_pays - remaining_oop
        self.member_pays = self.remaining_oop
        self.plan_pays += self.over_oop
        self.max_oop_met = True
        