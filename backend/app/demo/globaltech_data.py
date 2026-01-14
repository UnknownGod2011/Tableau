"""
Demo data generation for GlobalTech Industries
Creates realistic treasury data for a $500M portfolio across 5 subsidiaries
"""

from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import List, Dict
import random
import uuid

from app.models import (
    CorporateEntity, CashPosition, Investment, FXExposure,
    EntityType, AccountType, LiquidityTier, InstrumentType, 
    CreditRating, ExposureType
)


class GlobalTechDataGenerator:
    """Generate demo data for GlobalTech Industries"""
    
    def __init__(self):
        self.base_date = datetime.now(timezone.utc)
        self.entities = []
        self.cash_positions = []
        self.investments = []
        self.fx_exposures = []
    
    def generate_corporate_entities(self) -> List[CorporateEntity]:
        """Generate GlobalTech corporate structure"""
        # Parent company
        parent = CorporateEntity(
            entity_name="GlobalTech Industries Inc.",
            entity_type=EntityType.HEADQUARTERS,
            base_currency="USD",
            reporting_currency="USD",
            total_assets=Decimal("2500000000"),  # $2.5B
            annual_revenue=Decimal("1800000000"),  # $1.8B
            credit_rating="AA-",
            regulatory_jurisdiction="United States - SEC",
            treasury_policies={"max_single_investment": 50000000},
            created_by="demo_system"
        )
        
        # Subsidiaries
        subsidiaries = [
            {
                "name": "GlobalTech Europe Ltd.",
                "currency": "EUR",
                "jurisdiction": "United Kingdom - FCA",
                "assets": Decimal("800000000")
            },
            {
                "name": "GlobalTech Asia Pacific Pte Ltd.",
                "currency": "SGD", 
                "jurisdiction": "Singapore - MAS",
                "assets": Decimal("600000000")
            },
            {
                "name": "GlobalTech Canada Corp.",
                "currency": "CAD",
                "jurisdiction": "Canada - OSC", 
                "assets": Decimal("400000000")
            },
            {
                "name": "GlobalTech Japan KK",
                "currency": "JPY",
                "jurisdiction": "Japan - FSA",
                "assets": Decimal("300000000")
            }
        ]
        
        self.entities = [parent]
        
        for sub_data in subsidiaries:
            subsidiary = CorporateEntity(
                entity_name=sub_data["name"],
                entity_type=EntityType.SUBSIDIARY,
                base_currency=sub_data["currency"],
                reporting_currency="USD",
                total_assets=sub_data["assets"],
                regulatory_jurisdiction=sub_data["jurisdiction"],
                parent_entity_id=parent.id,
                created_by="demo_system"
            )
            self.entities.append(subsidiary)
        
        return self.entities
    
    def generate_cash_positions(self) -> List[CashPosition]:
        """Generate realistic cash positions for all entities"""
        cash_positions = []
        
        # Cash allocation by entity (as percentage of $300M cash portion of $500M treasury)
        # $300M cash + $200M investments = $500M total
        total_cash = Decimal("300000000")  # $300M in cash
        allocations = {
            0: 0.40,  # US HQ: 40% = $120M
            1: 0.25,  # Europe: 25% = $75M  
            2: 0.20,  # APAC: 20% = $60M
            3: 0.10,  # Canada: 10% = $30M
            4: 0.05,  # Japan: 5% = $15M
        }
        
        for i, entity in enumerate(self.entities):
            entity_allocation = Decimal(str(allocations[i])) * total_cash
            
            # Generate multiple cash accounts per entity
            accounts = self._generate_entity_cash_accounts(entity, entity_allocation)
            cash_positions.extend(accounts)
        
        self.cash_positions = cash_positions
        return cash_positions
    
    def _generate_entity_cash_accounts(self, entity: CorporateEntity, total_amount: Decimal) -> List[CashPosition]:
        """Generate cash accounts for a single entity"""
        accounts = []
        
        # Account distribution
        distributions = [
            {"type": AccountType.CHECKING, "pct": 0.15, "rate": 0.005},
            {"type": AccountType.SAVINGS, "pct": 0.25, "rate": 0.015},
            {"type": AccountType.MONEY_MARKET, "pct": 0.35, "rate": 0.025},
            {"type": AccountType.CERTIFICATE_DEPOSIT, "pct": 0.25, "rate": 0.035}
        ]
        
        for i, dist in enumerate(distributions):
            amount = total_amount * Decimal(str(dist["pct"]))
            
            account = CashPosition(
                entity_id=entity.id,
                account_number=f"{entity.base_currency}{random.randint(100000, 999999)}",
                account_name=f"{entity.entity_name} {dist['type'].value.title()} Account {i+1}",
                account_type=dist["type"],
                bank_name=self._get_bank_name(entity.base_currency),
                currency=entity.base_currency,
                balance=amount,
                available_balance=amount * Decimal("0.98"),  # 2% held for operations
                interest_rate=Decimal(str(dist["rate"])),
                liquidity_tier=self._get_liquidity_tier(dist["type"]),
                last_updated=self.base_date,
                created_by="demo_system"
            )
            accounts.append(account)
        
        return accounts
    
    def _get_bank_name(self, currency: str) -> str:
        """Get realistic bank names by currency"""
        banks = {
            "USD": ["JPMorgan Chase", "Bank of America", "Wells Fargo", "Citibank"],
            "EUR": ["Deutsche Bank", "BNP Paribas", "Santander", "ING Bank"],
            "SGD": ["DBS Bank", "OCBC Bank", "UOB", "Standard Chartered"],
            "CAD": ["Royal Bank of Canada", "TD Bank", "Bank of Montreal", "Scotiabank"],
            "JPY": ["Mitsubishi UFJ", "Sumitomo Mitsui", "Mizuho Bank", "SMBC"]
        }
        return random.choice(banks.get(currency, ["International Bank"]))
    
    def _get_liquidity_tier(self, account_type: AccountType) -> LiquidityTier:
        """Map account types to liquidity tiers"""
        mapping = {
            AccountType.CHECKING: LiquidityTier.IMMEDIATE,
            AccountType.SAVINGS: LiquidityTier.SHORT_TERM,
            AccountType.MONEY_MARKET: LiquidityTier.SHORT_TERM,
            AccountType.CERTIFICATE_DEPOSIT: LiquidityTier.MEDIUM_TERM,
            AccountType.TREASURY: LiquidityTier.LONG_TERM
        }
        return mapping.get(account_type, LiquidityTier.IMMEDIATE)
    
    def generate_investments(self) -> List[Investment]:
        """Generate investment portfolio"""
        investments = []
        
        # Investment allocation: $200M total across entities
        investment_templates = [
            {
                "name": "US Treasury 2Y Note",
                "type": InstrumentType.TREASURY_NOTE,
                "issuer": "US Treasury",
                "currency": "USD",
                "amount": Decimal("50000000"),
                "rate": Decimal("0.045"),
                "rating": CreditRating.AAA,
                "maturity_months": 24
            },
            {
                "name": "Corporate Bond - Apple Inc",
                "type": InstrumentType.CORPORATE_BOND,
                "issuer": "Apple Inc",
                "currency": "USD", 
                "amount": Decimal("25000000"),
                "rate": Decimal("0.038"),
                "rating": CreditRating.AA_PLUS,
                "maturity_months": 36
            },
            {
                "name": "Money Market Fund - Vanguard",
                "type": InstrumentType.MONEY_MARKET_FUND,
                "issuer": "Vanguard Group",
                "currency": "USD",
                "amount": Decimal("75000000"),
                "rate": Decimal("0.028"),
                "rating": CreditRating.AAA,
                "maturity_months": 3
            },
            {
                "name": "EUR Corporate Bond - Siemens AG",
                "type": InstrumentType.CORPORATE_BOND,
                "issuer": "Siemens AG",
                "currency": "EUR",
                "amount": Decimal("30000000"),
                "rate": Decimal("0.032"),
                "rating": CreditRating.A_PLUS,
                "maturity_months": 18
            },
            {
                "name": "Commercial Paper - Toyota",
                "type": InstrumentType.COMMERCIAL_PAPER,
                "issuer": "Toyota Motor Corp",
                "currency": "JPY",
                "amount": Decimal("20000000"),
                "rate": Decimal("0.015"),
                "rating": CreditRating.AA,
                "maturity_months": 6
            }
        ]
        
        for template in investment_templates:
            # Assign to appropriate entity based on currency
            entity = self._get_entity_by_currency(template["currency"])
            
            maturity_date = self.base_date + timedelta(days=template["maturity_months"] * 30)
            purchase_price = Decimal("100.00")  # Par value
            current_price = purchase_price * (Decimal("1.0") + (template["rate"] * Decimal("0.1")))
            
            investment = Investment(
                entity_id=entity.id,
                investment_name=template["name"],
                instrument_type=template["type"],
                issuer_name=template["issuer"],
                currency=template["currency"],
                principal_amount=template["amount"],
                purchase_price=purchase_price,
                current_price=current_price,
                market_value=template["amount"] * (current_price / purchase_price),
                coupon_rate=template["rate"],
                yield_to_maturity=template["rate"] * Decimal("1.05"),
                purchase_date=self.base_date - timedelta(days=random.randint(30, 365)),
                maturity_date=maturity_date,
                credit_rating=template["rating"],
                unrealized_gain_loss=template["amount"] * Decimal("0.02"),  # 2% unrealized gain
                created_by="demo_system"
            )
            investments.append(investment)
        
        self.investments = investments
        return investments
    
    def _get_entity_by_currency(self, currency: str) -> CorporateEntity:
        """Get entity that matches the currency"""
        for entity in self.entities:
            if entity.base_currency == currency:
                return entity
        return self.entities[0]  # Default to HQ
    
    def generate_fx_exposures(self) -> List[FXExposure]:
        """Generate FX exposures for currency risk management"""
        exposures = []
        
        # FX exposure scenarios
        exposure_templates = [
            {
                "name": "EUR Revenue Exposure",
                "type": ExposureType.TRANSACTION,
                "base": "USD",
                "exposure": "EUR", 
                "amount": Decimal("45000000"),
                "hedge_ratio": Decimal("0.75")
            },
            {
                "name": "JPY Operating Costs",
                "type": ExposureType.TRANSACTION,
                "base": "USD",
                "exposure": "JPY",
                "amount": Decimal("15000000"),
                "hedge_ratio": Decimal("0.50")
            },
            {
                "name": "CAD Investment Translation",
                "type": ExposureType.TRANSLATION,
                "base": "USD", 
                "exposure": "CAD",
                "amount": Decimal("25000000"),
                "hedge_ratio": Decimal("0.60")
            },
            {
                "name": "SGD Subsidiary Net Investment",
                "type": ExposureType.TRANSLATION,
                "base": "USD",
                "exposure": "SGD",
                "amount": Decimal("35000000"),
                "hedge_ratio": Decimal("0.40")
            }
        ]
        
        # Exchange rates (simplified for demo)
        fx_rates = {
            ("USD", "EUR"): Decimal("0.85"),
            ("USD", "JPY"): Decimal("150.0"),
            ("USD", "CAD"): Decimal("1.35"),
            ("USD", "SGD"): Decimal("1.32")
        }
        
        for template in exposure_templates:
            entity = self._get_entity_by_currency(template["base"])
            rate_key = (template["base"], template["exposure"])
            spot_rate = fx_rates.get(rate_key, Decimal("1.0"))
            
            base_equivalent = template["amount"] * spot_rate
            hedged_amount = template["amount"] * template["hedge_ratio"]
            
            exposure = FXExposure(
                entity_id=entity.id,
                exposure_name=template["name"],
                exposure_type=template["type"],
                base_currency=template["base"],
                exposure_currency=template["exposure"],
                notional_amount=template["amount"],
                base_currency_equivalent=base_equivalent,
                spot_rate=spot_rate,
                hedge_ratio=template["hedge_ratio"],
                hedged_amount=hedged_amount,
                unhedged_amount=template["amount"] - hedged_amount,
                exposure_date=self.base_date - timedelta(days=random.randint(1, 90)),
                maturity_date=self.base_date + timedelta(days=random.randint(90, 365)),
                unrealized_fx_gain_loss=base_equivalent * Decimal("0.015"),  # 1.5% FX gain
                created_by="demo_system"
            )
            exposures.append(exposure)
        
        self.fx_exposures = exposures
        return exposures
    
    def generate_all_demo_data(self) -> Dict:
        """Generate complete demo dataset"""
        return {
            "entities": self.generate_corporate_entities(),
            "cash_positions": self.generate_cash_positions(),
            "investments": self.generate_investments(), 
            "fx_exposures": self.generate_fx_exposures()
        }


def create_globaltech_demo_data() -> Dict:
    """Create complete GlobalTech Industries demo dataset"""
    generator = GlobalTechDataGenerator()
    return generator.generate_all_demo_data()


if __name__ == "__main__":
    # Generate and display demo data summary
    demo_data = create_globaltech_demo_data()
    
    print("GlobalTech Industries Demo Data Generated:")
    print(f"- Entities: {len(demo_data['entities'])}")
    print(f"- Cash Positions: {len(demo_data['cash_positions'])}")
    print(f"- Investments: {len(demo_data['investments'])}")
    print(f"- FX Exposures: {len(demo_data['fx_exposures'])}")
    
    total_cash = sum(pos.balance for pos in demo_data['cash_positions'])
    total_investments = sum(inv.market_value or inv.principal_amount for inv in demo_data['investments'])
    
    print(f"\nPortfolio Summary:")
    print(f"- Total Cash: ${total_cash:,.2f}")
    print(f"- Total Investments: ${total_investments:,.2f}")
    print(f"- Total Portfolio: ${total_cash + total_investments:,.2f}")