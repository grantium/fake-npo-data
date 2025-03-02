import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker()
# Add multiple locales for diverse names
Faker.seed(12345)
random.seed(12345)

class NonprofitDataGenerator:
    def __init__(self, 
                 start_date=datetime(2021, 1, 1),
                 end_date=datetime(2024, 12, 31),
                 num_constituents=2500,
                 num_funds=6,
                 num_campaigns=10,
                 transaction_volume_multiplier=1.0,
                 organization_percentage=0.15,
                 pledge_percentage=0.12):
        """
        Initialize the generator with configurable parameters.
        
        Args:
            start_date: Beginning of data range
            end_date: End of data range
            num_constituents: Total number of constituents to generate
            num_funds: Number of funds to generate
            num_campaigns: Number of campaigns to generate
            transaction_volume_multiplier: Multiply default transaction volumes
            organization_percentage: Percentage of constituents that are organizations
            pledge_percentage: Percentage of constituents with pledges
        """
        self.start_date = start_date
        self.end_date = end_date
        self.num_constituents = num_constituents
        self.num_funds = num_funds
        self.num_campaigns = num_campaigns
        self.transaction_volume_multiplier = transaction_volume_multiplier
        self.organization_percentage = organization_percentage
        self.pledge_percentage = pledge_percentage
        
        # Configure giving patterns
        self.giving_patterns = {
            'december_weight': 0.3,  # 30% of giving in December
            'giving_tuesday_weight': 0.1,  # 10% of giving on Giving Tuesday
            'appeal_response_rate': {
                'Direct Mail': 0.15,
                'Email': 0.08,
                'Event': 0.25,
                'Giving Tuesday': 0.20,
                'Phone': 0.12,
                'Social Media': 0.05,
                'Board Giving': 0.80,
                'Peer to Peer': 0.15
            }
        }
        
        # Initialize storage for generated data
        self.constituents = []
        self.households = []
        self.funds = []
        self.campaigns = []
        self.campaign_funds = []  # NEW: track campaign-fund associations
        self.appeals = []
        self.transactions = []
        self.donor_segments = {}  # NEW: track donor segments
        
        # Configure state distribution
        self.primary_states = ['CA', 'NY', 'IL']
        self.secondary_states = ['TX', 'FL', 'MA', 'WA', 'OR']
        self.state_weights = {
            'CA': 0.25, 'NY': 0.20, 'IL': 0.15,  # 60% from primary states
            'TX': 0.08, 'FL': 0.08, 'MA': 0.08, 'WA': 0.08, 'OR': 0.08  # 40% from secondary
        }

    def configure_giving_patterns(self, 
                                december_weight=0.3,
                                giving_tuesday_weight=0.1,
                                appeal_response_rates=None):
        """Customize giving pattern weights"""
        self.giving_patterns['december_weight'] = december_weight
        self.giving_patterns['giving_tuesday_weight'] = giving_tuesday_weight
        if appeal_response_rates:
            self.giving_patterns['appeal_response_rate'].update(appeal_response_rates)

    def configure_state_distribution(self, 
                                   primary_states=None,
                                   secondary_states=None,
                                   state_weights=None):
        """Customize geographic distribution"""
        if primary_states:
            self.primary_states = primary_states
        if secondary_states:
            self.secondary_states = secondary_states
        if state_weights:
            self.state_weights = state_weights

    def adjust_transaction_volumes(self, multiplier):
        """Adjust the volume of transactions generated"""
        self.transaction_volume_multiplier = multiplier

    def adjust_constituent_distribution(self, 
                                      org_percentage=0.15,
                                      pledge_percentage=0.12):
        """Adjust the distribution of constituent types"""
        self.organization_percentage = org_percentage
        self.pledge_percentage = pledge_percentage

    def generate_funds(self):
        fund_list = [
            {"fund_id": 1, "name": "General Operations", "description": "Supports daily operations and administrative needs"},
            {"fund_id": 2, "name": "Land Acquisition", "description": "Purchase of critical habitats and conservation lands"},
            {"fund_id": 3, "name": "Wildlife Protection", "description": "Species conservation and habitat restoration"},
            {"fund_id": 4, "name": "Climate Action", "description": "Initiatives addressing climate change impacts"},
            {"fund_id": 5, "name": "Environmental Education", "description": "Public awareness and educational programs"},
            {"fund_id": 6, "name": "Research & Science", "description": "Scientific research and field studies"},
            {"fund_id": 7, "name": "Policy & Advocacy", "description": "Environmental policy reform efforts"},
            {"fund_id": 8, "name": "Endowment Fund", "description": "Long-term sustainability and financial security"}
        ]
        self.funds = fund_list
        return pd.DataFrame(fund_list)

    def generate_constituent(self, is_organization=False):
        # Apply state weights to choose state more realistically
        state = np.random.choice(
            list(self.state_weights.keys()),
            p=list(self.state_weights.values())
        )
        
        if is_organization:
            org_types = ['Corporation', 'Foundation', 'Small Business', 'Government']
            org_type = random.choice(org_types)
            org_name = fake.company()
            
            return {
                'constituent_id': len(self.constituents) + 1,
                'type': 'Organization',
                'organization_name': org_name,
                'organization_type': org_type,
                'first_name': None,
                'last_name': None,
                'gender': None,
                'email': f"{fake.user_name()}@{org_name.lower().replace(' ', '')}.com",  # Better org emails
                'phone': fake.phone_number(),
                'address': fake.street_address(),
                'city': fake.city(),
                'state': state,
                'postal_code': fake.zipcode(),
                'creation_date': fake.date_between(
                    start_date=self.start_date,
                    end_date=self.end_date
                ),
                'lifetime_giving': 0.0,  # NEW: initialize lifetime giving
                'first_gift_date': None,  # NEW: track first gift date
                'last_gift_date': None    # NEW: track last gift date
            }
        else:
            # Updated gender distribution with non-binary option
            gender = np.random.choice(['F', 'M', 'NB'], p=[0.495, 0.495, 0.01])
            first_name = fake.first_name_female() if gender == 'F' else fake.first_name_male() if gender == 'M' else fake.first_name()
            last_name = fake.last_name()
            
            return {
                'constituent_id': len(self.constituents) + 1,
                'type': 'Individual',
                'organization_name': None,
                'organization_type': None,
                'first_name': first_name,
                'last_name': last_name,
                'gender': gender,
                'email': f"{first_name.lower()}.{last_name.lower()}@{fake.free_email_domain()}",  # More consistent emails
                'phone': fake.phone_number(),
                'address': fake.street_address(),
                'city': fake.city(),
                'state': state,
                'postal_code': fake.zipcode(),
                'creation_date': fake.date_between(
                    start_date=self.start_date,
                    end_date=self.end_date
                ),
                'lifetime_giving': 0.0,  # NEW: initialize lifetime giving
                'first_gift_date': None,  # NEW: track first gift date
                'last_gift_date': None    # NEW: track last gift date
            }

    def generate_constituents(self, num_constituents=2500):
        num_organizations = int(num_constituents * self.organization_percentage)
        num_individuals = num_constituents - num_organizations
        
        # Generate organizations
        for _ in range(num_organizations):
            self.constituents.append(self.generate_constituent(is_organization=True))
            
        # Generate individuals
        for _ in range(num_individuals):
            self.constituents.append(self.generate_constituent(is_organization=False))
        
        # Assign constituents to segments
        self.create_donor_segments()
        
        return pd.DataFrame(self.constituents)

    def create_donor_segments(self):
        """Assign constituents to donor segments for later use in transaction generation"""
        # Create random segments that will influence giving patterns
        for constituent in self.constituents:
            # Assign giving frequency segment
            frequency = np.random.choice(
                ['One-time', 'Occasional', 'Regular', 'Loyal'],
                p=[0.4, 0.3, 0.2, 0.1]
            )
            
            # Assign giving level segment (will influence amount)
            if constituent['type'] == 'Organization':
                level = np.random.choice(
                    ['Small', 'Medium', 'Major', 'Principal'],
                    p=[0.3, 0.4, 0.2, 0.1]
                )
            else:
                level = np.random.choice(
                    ['Small', 'Medium', 'Major', 'Principal'],
                    p=[0.7, 0.2, 0.07, 0.03]
                )
            
            # Store segments
            self.donor_segments[constituent['constituent_id']] = {
                'frequency': frequency,
                'level': level,
                'giving_trend': np.random.choice(['Decreasing', 'Stable', 'Increasing'], p=[0.2, 0.5, 0.3]),
                'cause_affinity': random.sample([f['fund_id'] for f in self.funds], k=2)  # Top 2 causes they care about
            }

    def generate_households(self):
        # Generate households for individuals
        individual_constituents = [c for c in self.constituents if c['type'] == 'Individual']
        household_id = 1
        households = []
        assigned_constituents = set()

        # First, create households for couples
        for i in range(len(individual_constituents)):
            if i in assigned_constituents:
                continue
                
            constituent = individual_constituents[i]
            
            # 75% chance of being in a multi-person household
            if random.random() < 0.75:
                # Find a suitable partner if possible
                potential_partners = []
                for j in range(i+1, min(i+10, len(individual_constituents))):
                    if j not in assigned_constituents:
                        potential_partners.append(j)
                
                if potential_partners:
                    # Select a partner
                    partner_idx = random.choice(potential_partners)
                    partner = individual_constituents[partner_idx]
                    
                    # Determine if it's a same-sex couple (5-10% chance)
                    same_sex_couple = random.random() < 0.075  # 7.5% chance
                    
                    # If same-sex couple, but partners have different genders, try to find another partner
                    if same_sex_couple and constituent['gender'] != partner['gender']:
                        same_gender_partners = []
                        for j in range(i+1, min(i+20, len(individual_constituents))):
                            if j not in assigned_constituents and individual_constituents[j]['gender'] == constituent['gender']:
                                same_gender_partners.append(j)
                        
                        if same_gender_partners:
                            partner_idx = random.choice(same_gender_partners)
                            partner = individual_constituents[partner_idx]
                    
                    # Determine if partners have different last names (30% chance)
                    different_last_names = random.random() < 0.3
                    
                    # Create household name based on partners
                    if different_last_names:
                        # Randomly determine order of names
                        if random.random() < 0.5:
                            household_name = f"{constituent['first_name']} {constituent['last_name']} & {partner['first_name']} {partner['last_name']}"
                        else:
                            household_name = f"{partner['first_name']} {partner['last_name']} & {constituent['first_name']} {constituent['last_name']}"
                    else:
                        # Both use the same last name
                        # Randomly choose which last name to use
                        if random.random() < 0.5:
                            shared_last_name = constituent['last_name']
                        else:
                            shared_last_name = partner['last_name']
                        
                        # Check gender of couple for traditional naming
                        if not same_sex_couple and ((constituent['gender'] == 'M' and partner['gender'] == 'F') or 
                                                (constituent['gender'] == 'F' and partner['gender'] == 'M')):
                            # Traditional Mr. & Mrs. format (70% chance)
                            if random.random() < 0.7:
                                if constituent['gender'] == 'M':
                                    household_name = f"Mr. & Mrs. {constituent['first_name']} {shared_last_name}"
                                else:
                                    household_name = f"Mr. & Mrs. {partner['first_name']} {shared_last_name}"
                            else:
                                # First names with shared last name
                                if random.random() < 0.5:
                                    household_name = f"{constituent['first_name']} & {partner['first_name']} {shared_last_name}"
                                else:
                                    household_name = f"{partner['first_name']} & {constituent['first_name']} {shared_last_name}"
                        else:
                            # For same-sex or non-binary couples, use first names
                            if random.random() < 0.5:
                                household_name = f"{constituent['first_name']} & {partner['first_name']} {shared_last_name}"
                            else:
                                household_name = f"{partner['first_name']} & {constituent['first_name']} {shared_last_name}"
                    
                    # Create primary household record
                    households.append({
                        'household_id': household_id,
                        'name': household_name,
                        'constituent_id': constituent['constituent_id'],  # Changed field name
                        'primary_constituent_id': constituent['constituent_id'],
                        'is_primary': True,  # New field
                        'address': constituent['address'],
                        'city': constituent['city'],
                        'state': constituent['state'],
                        'postal_code': constituent['postal_code'],
                        'creation_date': constituent['creation_date']
                    })
                    
                    # Create household member record for partner
                    households.append({
                        'household_id': household_id,
                        'name': household_name,
                        'constituent_id': partner['constituent_id'],  # Partner ID
                        'primary_constituent_id': constituent['constituent_id'],
                        'is_primary': False,  # Not primary
                        'address': constituent['address'],
                        'city': constituent['city'],
                        'state': constituent['state'],
                        'postal_code': constituent['postal_code'],
                        'creation_date': constituent['creation_date']
                    })
                    
                    # Add to assigned constituents
                    assigned_constituents.add(i)
                    assigned_constituents.add(partner_idx)
                    
                    # Random household size (additional members beyond the couple, 0-3 more)
                    additional_members = random.choices([0, 1, 2, 3], weights=[60, 25, 10, 5])[0]
                    
                    # Add additional members if needed
                    members_added = 0
                    search_idx = max(i, partner_idx) + 1
                    while members_added < additional_members and search_idx < len(individual_constituents):
                        if search_idx not in assigned_constituents:
                            additional_member = individual_constituents[search_idx]
                            # Add household record for additional member
                            households.append({
                                'household_id': household_id,
                                'name': household_name,
                                'constituent_id': additional_member['constituent_id'],
                                'primary_constituent_id': constituent['constituent_id'],
                                'is_primary': False,
                                'address': constituent['address'],
                                'city': constituent['city'],
                                'state': constituent['state'],
                                'postal_code': constituent['postal_code'],
                                'creation_date': constituent['creation_date']
                            })
                            assigned_constituents.add(search_idx)
                            members_added += 1
                        search_idx += 1
                            
                    household_id += 1
                else:
                    # No partner available, create single household with formal title
                    household_name = self.get_formal_name(constituent)
                    households.append({
                        'household_id': household_id,
                        'name': household_name,
                        'constituent_id': constituent['constituent_id'],
                        'primary_constituent_id': constituent['constituent_id'],
                        'is_primary': True,
                        'address': constituent['address'],
                        'city': constituent['city'],
                        'state': constituent['state'],
                        'postal_code': constituent['postal_code'],
                        'creation_date': constituent['creation_date']
                    })
                    assigned_constituents.add(i)
                    household_id += 1
            else:
                # Create single-person household with formal title
                household_name = self.get_formal_name(constituent)
                households.append({
                    'household_id': household_id,
                    'name': household_name,
                    'constituent_id': constituent['constituent_id'],
                    'primary_constituent_id': constituent['constituent_id'],
                    'is_primary': True,
                    'address': constituent['address'],
                    'city': constituent['city'],
                    'state': constituent['state'],
                    'postal_code': constituent['postal_code'],
                    'creation_date': constituent['creation_date']
                })
                assigned_constituents.add(i)
                household_id += 1
                    
        # Create single-person households for remaining constituents
        for i in range(len(individual_constituents)):
            if i not in assigned_constituents:
                constituent = individual_constituents[i]
                household_name = self.get_formal_name(constituent)
                households.append({
                    'household_id': household_id,
                    'name': household_name,
                    'constituent_id': constituent['constituent_id'],
                    'primary_constituent_id': constituent['constituent_id'],
                    'is_primary': True,
                    'address': constituent['address'],
                    'city': constituent['city'],
                    'state': constituent['state'],
                    'postal_code': constituent['postal_code'],
                    'creation_date': constituent['creation_date']
                })
                household_id += 1
                    
        self.households = households
        return pd.DataFrame(households)

    def get_formal_name(self, constituent):
        """Generate a formal name for a single-person household"""
        gender = constituent['gender']
        if gender == 'F':
            title = random.choices(['Ms.', 'Mrs.', 'Miss'], weights=[0.6, 0.3, 0.1])[0]
        elif gender == 'M':
            title = 'Mr.'
        else:  # NB or None
            title = 'Mx.'  # Gender-neutral title
            
        return f"{title} {constituent['first_name']} {constituent['last_name']}"
        def create_formal_single_household(self, constituent, household_id):
            """Helper function to create formal single-person household name"""
            gender = constituent['gender']
            if gender == 'F':
                title = random.choices(['Ms.', 'Mrs.', 'Miss'], weights=[0.6, 0.3, 0.1])[0]
            elif gender == 'M':
                title = 'Mr.'
            else:  # NB or None
                title = 'Mx.'  # Gender-neutral title
                
            return {
                'household_id': household_id,
                'name': f"{title} {constituent['first_name']} {constituent['last_name']}",
                'primary_constituent_id': constituent['constituent_id'],
                'address': constituent['address'],
                'city': constituent['city'],
                'state': constituent['state'],
                'postal_code': constituent['postal_code'],
                'creation_date': constituent['creation_date']
            }


    def generate_campaigns(self):
        campaign_types = [
                ('Annual', 'Earth Protectors Annual Fund'),
                ('Capital', 'Wildlands Corridor Acquisition'),
                ('Special', 'Forest Fire Recovery'),
                ('Program', 'Ocean Plastics Initiative'),
                ('Special', 'Endangered Species Protection'),
                ('Program', 'Youth Environmental Leadership'),
                ('Program', 'Native Plant Restoration'),
                ('Special', 'Clean Water Action'),
                ('Capital', 'Conservation Science Center'),
                ('Annual', 'Year-End Sustainability Drive'),
                ('Program', 'Community Garden Network'),
                ('Special', 'Renewable Energy Transition'),
                
                # Event Campaigns
                ('Event', 'Green Gala Annual Dinner'),
                ('Event', 'Trail Blazer 5K Run/Walk'),
                ('Event', 'Hike-a-Thon: Miles for Wildlife'),
                ('Event', 'Eco Film Festival'),
                ('Event', 'River Cleanup Day'),
                ('Event', 'Sustainable Living Expo'),
                ('Event', 'Polar Plunge for Climate Action'),
                ('Event', 'Cycling for Conservation'),
                ('Event', 'Moonlight Paddle Fundraiser'),
                ('Event', 'Bird-a-Thon Counting Challenge'),
                ('Event', 'Tree Planting Day'),
                ('Event', 'Nature Photography Auction')
            ]        
        campaigns = []
        campaign_id = 1
        campaign_fund_mappings = []
        
        # Define fund relevance for campaign types
        campaign_fund_affinities = {
            'Annual': [1, 8],  # General Operations, Endowment
            'Capital': [2, 8],  # Land Acquisition, Endowment
            'Special': [3, 4, 7],  # Wildlife Protection, Climate Action, Policy
            'Program': [5, 6],  # Environmental Education, Research
            'Event': [1, 3, 4, 5]  # Various funds
        }
        
        for campaign_type, name in campaign_types:
            # Determine campaign duration based on type
            if campaign_type == 'Annual':
                start_date = fake.date_between(start_date=self.start_date, 
                                            end_date=self.end_date - timedelta(days=365))
                end_date = start_date + timedelta(days=365)
            elif campaign_type == 'Capital':
                start_date = fake.date_between(start_date=self.start_date, 
                                            end_date=self.end_date - timedelta(days=730))
                end_date = start_date + timedelta(days=730)
            else:
                start_date = fake.date_between(start_date=self.start_date, 
                                            end_date=self.end_date - timedelta(days=180))
                end_date = start_date + timedelta(days=180)
                
            # Create campaign
            campaigns.append({
                'campaign_id': campaign_id,
                'name': name,
                'type': campaign_type,
                'start_date': start_date,
                'end_date': end_date,
                'goal_amount': random.choice([50000, 100000, 250000, 500000, 1000000]),
                'description': f"Campaign for {name}"
            })
            
            # Associate campaign with relevant funds (NEW)
            # Each campaign is associated with 1-3 funds based on campaign type
            relevant_funds = campaign_fund_affinities.get(campaign_type, [1])  # Default to General Fund
            num_funds = min(len(relevant_funds), random.randint(1, 3))
            
            # Select funds and create mappings with weights
            selected_funds = random.sample(relevant_funds, num_funds)
            
            # Ensure all campaigns have at least one fund
            if not selected_funds:
                selected_funds = [1]  # Assign to General Operations if nothing else fits
                
            # Create weighted mappings (primary fund gets higher weight)
            weights = [0.7, 0.2, 0.1][:num_funds]
            if len(weights) < num_funds:
                remaining = num_funds - len(weights)
                weights.extend([0.1/remaining] * remaining)
                
            for i, fund_id in enumerate(selected_funds):
                campaign_fund_mappings.append({
                    'campaign_id': campaign_id,
                    'fund_id': fund_id,
                    'weight': weights[i],  # Primary fund gets higher weight
                    'is_primary': i == 0    # First fund is primary
                })
            
            campaign_id += 1
        
        self.campaigns = campaigns
        self.campaign_funds = campaign_fund_mappings
        
        return pd.DataFrame(campaigns), pd.DataFrame(campaign_fund_mappings)

    def generate_appeals(self):
        # Create more realistic mapping between appeal types and campaign types
        appeal_type_mapping = {
            'Annual': ['Direct Mail', 'Email Campaign', 'Phone-a-thon', 'Giving Tuesday', 'Monthly Giving Program'],
            'Capital': ['Major Donor Cultivation', 'Corporate Partnerships', 'Board Giving', 'Grant Application'],
            'Special': ['Social Media Challenge', 'Peer to Peer', 'Email Campaign', 'Volunteer Fundraising'],
            'Program': ['Grant Application', 'Email Campaign', 'Direct Mail', 'Monthly Giving Program'],
            'Event': ['Event', 'Peer to Peer', 'Social Media Challenge', 'Corporate Partnerships']
        }
        
        appeals = []
        appeal_id = 1
        
        for campaign in self.campaigns:
            # Determine relevant appeal types for this campaign
            relevant_appeal_types = appeal_type_mapping.get(campaign['type'], ['Direct Mail', 'Email Campaign'])
            
            # Generate 2-4 appeals per campaign with relevant types
            num_appeals = random.randint(2, 4)
            campaign_duration = (campaign['end_date'] - campaign['start_date']).days
            
            # Check if campaign includes December (for seasonal patterns)
            includes_december = (campaign['start_date'].month <= 12 and campaign['end_date'].month >= 12) or \
                                (campaign['start_date'].month > campaign['end_date'].month and campaign['end_date'].year > campaign['start_date'].year)
            
            # Check if campaign includes November (for Giving Tuesday)
            includes_november = (campaign['start_date'].month <= 11 and campaign['end_date'].month >= 11) or \
                            (campaign['start_date'].month > campaign['end_date'].month and campaign['end_date'].year > campaign['start_date'].year)
            
            # Add a December appeal if campaign includes December
            if includes_december and 'Direct Mail' in relevant_appeal_types:
                year = max(min(campaign['end_date'].year, 2024), 2021)
                december_start = datetime(year, 12, 1).date()  # Convert to date
                december_end = datetime(year, 12, 31).date()   # Convert to date
                
                # Make sure we're comparing dates to dates
                campaign_start_date = campaign['start_date'].date() if isinstance(campaign['start_date'], datetime) else campaign['start_date']
                campaign_end_date = campaign['end_date'].date() if isinstance(campaign['end_date'], datetime) else campaign['end_date']
                
                if december_start <= campaign_end_date and december_end >= campaign_start_date:
                    appeals.append({
                        'appeal_id': appeal_id,
                        'campaign_id': campaign['campaign_id'],
                        'name': f"Year-End Appeal - {campaign['name']}",
                        'type': 'Direct Mail',
                        'seasonal': 'December',
                        'start_date': december_start,
                        'end_date': december_end,
                        'goal_amount': random.choice([10000, 25000, 50000, 100000]),
                        'description': f"Year-end appeal for {campaign['name']}"
                    })
                    appeal_id += 1
            
            # Add a Giving Tuesday appeal if campaign includes November
            if includes_november and campaign['type'] in ['Annual', 'Special', 'Program']:
                # Calculate Giving Tuesday (first Tuesday after Thanksgiving in the US) - simplified approach
                year = max(min(campaign['end_date'].year, 2024), 2021)
                giving_tuesday = datetime(year, 11, 30).date()  # Convert to date
                
                # Make sure we're comparing dates to dates
                campaign_start_date = campaign['start_date'].date() if isinstance(campaign['start_date'], datetime) else campaign['start_date']
                campaign_end_date = campaign['end_date'].date() if isinstance(campaign['end_date'], datetime) else campaign['end_date']
                
                if giving_tuesday <= campaign_end_date and giving_tuesday >= campaign_start_date:
                    appeals.append({
                        'appeal_id': appeal_id,
                        'campaign_id': campaign['campaign_id'],
                        'name': f"Giving Tuesday - {campaign['name']}",
                        'type': 'Giving Tuesday',
                        'seasonal': 'Giving Tuesday',
                        'start_date': (datetime(year, 11, 30) - timedelta(days=7)).date(),  # Convert to date
                        'end_date': (datetime(year, 11, 30) + timedelta(days=1)).date(),   # Convert to date
                        'goal_amount': random.choice([5000, 10000, 25000]),
                        'description': f"Giving Tuesday appeal for {campaign['name']}"
                    })
                    appeal_id += 1
            
            # Generate regular appeals spread throughout the campaign
            for i in range(num_appeals):
                # Choose an appeal type that makes sense for this campaign
                appeal_type = random.choice(relevant_appeal_types)
                
                # Spread appeals throughout campaign duration
                appeal_start = campaign['start_date'] + timedelta(
                    days=int((campaign_duration / (num_appeals + 1)) * (i + 1))
                )
                
                # Appeal duration based on type
                if appeal_type == 'Event':
                    appeal_duration = 1  # One day for events
                elif appeal_type in ['Email Campaign', 'Giving Tuesday', 'Social Media Challenge']:
                    appeal_duration = random.randint(1, 14)  # Short duration
                else:
                    appeal_duration = random.randint(14, 45)  # Longer duration
                
                appeals.append({
                    'appeal_id': appeal_id,
                    'campaign_id': campaign['campaign_id'],
                    'name': f"{appeal_type} - {campaign['name']}",
                    'type': appeal_type,
                    'seasonal': 'Regular',
                    'start_date': appeal_start,
                    'end_date': appeal_start + timedelta(days=appeal_duration),
                    'goal_amount': random.choice([5000, 10000, 25000, 50000]),
                    'description': f"{appeal_type} appeal for {campaign['name']}"
                })
                appeal_id += 1
        
        self.appeals = appeals
        return pd.DataFrame(appeals)

    def generate_transaction_amount(self, constituent_id, appeal_type):
        """Generate realistic transaction amounts based on constituent type, appeal, and donor segment"""
        constituent = next(c for c in self.constituents if c['constituent_id'] == constituent_id)
        constituent_type = constituent['type']
        
        # Get donor segment
        segment = self.donor_segments.get(constituent_id, {
            'level': 'Small',
            'frequency': 'One-time',
            'giving_trend': 'Stable'
        })
        
        # Base amount ranges based on donor level segment
        level_ranges = {
            'Organization': {
                'Small': (100, 500),
                'Medium': (501, 2500),
                'Major': (2501, 10000),
                'Principal': (10001, 100000)
            },
            'Individual': {
                'Small': (5, 100),
                'Medium': (101, 500),
                'Major': (501, 2500),
                'Principal': (2501, 25000)
            }
        }
        
        # Get appropriate range
        type_ranges = level_ranges.get(constituent_type, level_ranges['Individual'])
        min_amt, max_amt = type_ranges.get(segment['level'], type_ranges['Small'])
        
        # Adjust amount based on appeal type
        multipliers = {
            'Giving Tuesday': 1.3,
            'Event': 1.5,
            'Board Giving': 2.0,
            'Direct Mail': 0.8,
            'Email': 0.7,
            'Major Donor Cultivation': 3.0,
            'Corporate Partnerships': 2.5,
            'Peer to Peer': 0.9
        }
        multiplier = multipliers.get(appeal_type, 1.0)
        
        # Further adjust based on giving trend
        trend_multipliers = {
            'Increasing': 1.2,
            'Stable': 1.0,
            'Decreasing': 0.8
        }
        trend_multiplier = trend_multipliers.get(segment['giving_trend'], 1.0)
        
        # Apply all multipliers and generate amount
        amount = round(random.uniform(min_amt, max_amt) * multiplier * trend_multiplier, 2)
        
        # Apply transaction volume multiplier
        amount *= self.transaction_volume_multiplier
        
        return amount

    def generate_payment_method(self, constituent_type, amount):
        """Generate payment method based on realistic distribution, constituent type and amount"""
        if constituent_type == 'Organization':
            if amount >= 5000:
                methods = {'Check': 0.60, 'ACH': 0.35, 'Other': 0.05}
            else:
                methods = {'Credit Card': 0.30, 'Check': 0.50, 'ACH': 0.18, 'Other': 0.02}
        else:  # Individual
            if amount >= 1000:
                methods = {'Credit Card': 0.40, 'Check': 0.45, 'ACH': 0.12, 'Other': 0.03}
            else:
                methods = {'Credit Card': 0.65, 'Check': 0.20, 'ACH': 0.08, 'Cash': 0.05, 'Other': 0.02}
        
        return random.choices(list(methods.keys()), list(methods.values()))[0]

    def select_fund_for_transaction(self, campaign_id):
        """Select a fund for a transaction based on campaign-fund mappings"""
        # Find associated funds for this campaign
        campaign_funds = [cf for cf in self.campaign_funds if cf['campaign_id'] == campaign_id]
        
        if not campaign_funds:
            # If no specific funds mapped, use general fund
            return 1
        
        # Select based on weights
        fund_ids = [cf['fund_id'] for cf in campaign_funds]
        weights = [cf['weight'] for cf in campaign_funds]
        
        return random.choices(fund_ids, weights=weights)[0]

    def generate_transactions(self):
        """Generate transactions for all constituents across appeals with seasonal patterns"""
        transactions = []
        transaction_id = 1
        
        # Calculate donor retention and acquisition rates per year
        years = range(self.start_date.year, self.end_date.year + 1)
        active_donors_by_year = {year: set() for year in years}
        
        for appeal in self.appeals:
            # Get the campaign associated with this appeal
            campaign_id = appeal['campaign_id']
            campaign = next(c for c in self.campaigns if c['campaign_id'] == campaign_id)
            
            # Determine if this is a seasonal appeal
            is_december_appeal = appeal.get('seasonal') == 'December'
            is_giving_tuesday = appeal.get('seasonal') == 'Giving Tuesday'
                
            # Adjust response rate based on appeal type and seasonality
            base_response_rate = self.giving_patterns['appeal_response_rate'].get(
                appeal['type'], 0.10
            )
            
            # Boost response rate for seasonal appeals
            if is_december_appeal:
                response_rate = base_response_rate * (1 + self.giving_patterns['december_weight'])
            elif is_giving_tuesday:
                response_rate = base_response_rate * (1 + self.giving_patterns['giving_tuesday_weight'])
            else:
                response_rate = base_response_rate
                
            # Calculate appeal period
            appeal_start = appeal['start_date']
            appeal_end = appeal['end_date']
            year = appeal_start.year
            
            # Calculate potential donors (based on existing constituents at that time)
            potential_donors = [c for c in self.constituents 
                            if c['creation_date'] <= appeal_end]
            
            # Determine number of donors for this appeal based on response rate
            num_donors = int(len(potential_donors) * response_rate * self.transaction_volume_multiplier)
            
            # Weight selection toward donors with affinity for this campaign's funds
            donor_weights = []
            for donor in potential_donors:
                donor_id = donor['constituent_id']
                segment = self.donor_segments.get(donor_id, {})
                
                # Check if donor has affinity for campaign's primary fund
                campaign_funds = [cf for cf in self.campaign_funds if cf['campaign_id'] == campaign_id and cf['is_primary']]
                primary_fund = campaign_funds[0]['fund_id'] if campaign_funds else 1
                
                # Default weight
                weight = 1.0
                
                # Increase weight for donors with cause affinity
                cause_affinity = segment.get('cause_affinity', [])
                if primary_fund in cause_affinity:
                    weight *= 3.0
                    
                # Adjust weight based on giving frequency
                frequency_weights = {
                    'One-time': 0.7,
                    'Occasional': 1.0,
                    'Regular': 2.0,
                    'Loyal': 3.0
                }
                weight *= frequency_weights.get(segment.get('frequency', 'One-time'), 1.0)
                
                donor_weights.append(weight)
            
            # Select donors for this appeal using weights
            if not potential_donors:
                continue
                
            # Normalize weights
            total_weight = sum(donor_weights) or 1  # Avoid division by zero
            normalized_weights = [w/total_weight for w in donor_weights]
            
            # Determine how many donors to select
            num_donors = min(num_donors, len(potential_donors))
            
            # Select donors using weighted probability
            selected_indices = random.choices(
                range(len(potential_donors)),
                weights=normalized_weights, 
                k=num_donors
            )
            
            appeal_donors = [potential_donors[i] for i in selected_indices]
            
            for donor in appeal_donors:
                # Determine if donor makes multiple gifts to this appeal
                donor_frequency = self.donor_segments.get(donor['constituent_id'], {}).get('frequency', 'One-time')
                multi_gift_probs = {
                    'One-time': 0.001,
                    'Occasional': 0.005,
                    'Regular': 0.01,
                    'Loyal': 0.05
                }
                multi_gift_prob = multi_gift_probs.get(donor_frequency, 0.05)
                num_gifts = 1
                if random.random() < multi_gift_prob:
                    num_gifts = random.choices([2, 3], weights=[0.8, 0.2])[0]
                
                for gift_num in range(num_gifts):
                    # Generate transaction date
                    if appeal['type'] == 'Event':
                        transaction_date = appeal_end
                    else:
                        # Generate date within appeal period with slight weighting toward end
                        days_range = (appeal_end - appeal_start).days
                        if days_range <= 0:
                            transaction_date = appeal_start
                        else:
                            day_offset = int(random.triangular(0, days_range, days_range * 0.8))
                            transaction_date = appeal_start + timedelta(days=day_offset)
                    
                    # Select fund based on campaign-fund mappings
                    fund_id = self.select_fund_for_transaction(campaign_id)
                    
                    # Generate amount based on donor segment and appeal type
                    amount = self.generate_transaction_amount(donor['constituent_id'], appeal['type'])
                    
                    # For repeat gifts in same appeal, reduce the amount
                    if gift_num > 0:
                        amount = amount * 0.7  # 70% of original amount for subsequent gifts
                    
                    # Generate payment method
                    payment_method = self.generate_payment_method(donor['type'], amount)
                    
                    transaction = {
                        'transaction_id': transaction_id,
                        'constituent_id': donor['constituent_id'],
                        'appeal_id': appeal['appeal_id'],
                        'campaign_id': campaign_id,
                        'fund_id': fund_id,
                        'date': transaction_date,
                        'amount': amount,
                        'payment_method': payment_method,
                        'type': 'Gift',
                        'status': 'Completed'
                    }
                    
                    transactions.append(transaction)
                    transaction_id += 1
                    
                    # Update donor lifetime metrics
                    self.update_donor_metrics(donor['constituent_id'], amount, transaction_date)
                    
                    # Add donor to active donors for the year
                    active_donors_by_year[year].add(donor['constituent_id'])
        
        self.transactions = transactions
        return pd.DataFrame(transactions)
    
    def update_donor_metrics(self, constituent_id, amount, date):
        """Update donor lifetime giving metrics"""
        for constituent in self.constituents:
            if constituent['constituent_id'] == constituent_id:
                # Update lifetime giving
                constituent['lifetime_giving'] += amount
                
                # Update first gift date if not set
                if constituent['first_gift_date'] is None:
                    constituent['first_gift_date'] = date
                    
                # Update last gift date
                constituent['last_gift_date'] = max(constituent['last_gift_date'] or date, date)
                
                break

    def generate_pledges(self):
        """Generate pledges for a subset of donors"""
        pledges = []
        pledge_payments = []
        pledge_id = 1
        payment_id = 1
        
        # Identify donors with strong giving history
        donors_with_transactions = {}
        for transaction in self.transactions:
            donor_id = transaction['constituent_id']
            if donor_id not in donors_with_transactions:
                donors_with_transactions[donor_id] = []
            donors_with_transactions[donor_id].append(transaction)
        
        # Select donors with at least 2 gifts for pledges
        eligible_donors = [donor_id for donor_id, transactions in donors_with_transactions.items() 
                        if len(transactions) >= 2]
        
        # Determine number of pledge donors
        num_pledge_donors = int(len(eligible_donors) * self.pledge_percentage)
        
        if not eligible_donors or num_pledge_donors == 0:
            # Return empty dataframes if no eligible donors
            return pd.DataFrame(columns=[
                'pledge_id', 'constituent_id', 'campaign_id', 'total_amount',
                'installment_amount', 'start_date', 'frequency', 'installments', 'status'
            ]), pd.DataFrame(columns=[
                'payment_id', 'pledge_id', 'amount', 'date', 'status'
            ])
            
        pledge_donors = random.sample(eligible_donors, min(num_pledge_donors, len(eligible_donors)))
        
        # Get current date for comparisons - convert to date object
        current_date = datetime.now().date()
        
        for donor_id in pledge_donors:
            # Find donor info
            donor = next(c for c in self.constituents if c['constituent_id'] == donor_id)
            
            # Find donor's transactions to determine appropriate pledge amount
            donor_transactions = donors_with_transactions[donor_id]
            avg_gift = sum(t['amount'] for t in donor_transactions) / len(donor_transactions)
            
            # Determine pledge type based on donor segment
            segment = self.donor_segments.get(donor_id, {'frequency': 'One-time', 'level': 'Small'})
            
            # Pledge frequency based on donor frequency segment
            frequency_mapping = {
                'One-time': ['Annual'],
                'Occasional': ['Annual', 'Quarterly'],
                'Regular': ['Monthly', 'Quarterly'],
                'Loyal': ['Monthly', 'Quarterly', 'Annual']
            }
            
            pledge_frequencies = frequency_mapping.get(segment['frequency'], ['Annual'])
            pledge_type = random.choice(pledge_frequencies)
            
            # Generate pledge details
            # Ensure start date is after donor's creation date and first gift
            earlier_date_1 = donor['creation_date']
            earlier_date_1 = earlier_date_1.date() if isinstance(earlier_date_1, datetime) else earlier_date_1
            
            earlier_date_2 = donor['first_gift_date'] or donor['creation_date']
            earlier_date_2 = earlier_date_2.date() if isinstance(earlier_date_2, datetime) else earlier_date_2
            
            earliest_start = max(earlier_date_1, earlier_date_2)
            
            try:
                end_date_limit = self.end_date.date() if isinstance(self.end_date, datetime) else self.end_date
                start_date = fake.date_between(
                    start_date=earliest_start,
                    end_date=end_date_limit - timedelta(days=90)
                )
            except:
                # If date range is invalid, use earliest_start
                start_date = earliest_start
            
            if pledge_type == 'Monthly':
                installments = random.choice([12, 24, 36])
                frequency = 'Monthly'
            elif pledge_type == 'Quarterly':
                installments = random.choice([4, 8])
                frequency = 'Quarterly'
            else:  # Annual
                installments = random.choice([1, 2, 3])
                frequency = 'Annual'
                
            # Generate pledge amount
            # For monthly/quarterly pledges, make installment amount ~1.5x their average gift
            # For annual pledges, make it ~5x their average gift
            if frequency == 'Monthly':
                installment_amount = round(avg_gift * 1.5, 2)
            elif frequency == 'Quarterly': 
                installment_amount = round(avg_gift * 3, 2)
            else:  # Annual
                installment_amount = round(avg_gift * 5, 2)
                
            total_amount = round(installment_amount * installments, 2)
            
            # Select a campaign for this pledge
            active_campaigns = []
            for campaign in self.campaigns:
                campaign_start = campaign['start_date'].date() if isinstance(campaign['start_date'], datetime) else campaign['start_date']
                campaign_end = campaign['end_date'].date() if isinstance(campaign['end_date'], datetime) else campaign['end_date']
                
                start_date_for_comparison = start_date.date() if isinstance(start_date, datetime) else start_date
                
                if campaign_start <= start_date_for_comparison <= campaign_end:
                    active_campaigns.append(campaign)
            
            if not active_campaigns:
                # If no active campaigns, use a random one
                campaign_id = random.choice(self.campaigns)['campaign_id']
            else:
                campaign_id = random.choice(active_campaigns)['campaign_id']
            
            # Determine pledge status
            # Calculate end date
            if frequency == 'Monthly':
                end_date = start_date + timedelta(days=30 * installments)
            elif frequency == 'Quarterly':
                end_date = start_date + timedelta(days=90 * installments)
            else:  # Annual
                end_date = start_date + timedelta(days=365 * installments)
            
            # Convert to date object for comparison if needed
            end_date = end_date.date() if isinstance(end_date, datetime) else end_date
            
            if end_date > current_date:  # Fixed comparison
                # Pledge is still active
                status = random.choices(['Active', 'Cancelled'], weights=[0.9, 0.1])[0]
            else:
                # Pledge should be completed
                status = random.choices(['Completed', 'Cancelled'], weights=[0.85, 0.15])[0]
                
            pledge = {
                'pledge_id': pledge_id,
                'constituent_id': donor_id,
                'campaign_id': campaign_id,
                'total_amount': total_amount,
                'installment_amount': installment_amount,
                'start_date': start_date,
                'frequency': frequency,
                'installments': installments,
                'status': status
            }
            pledges.append(pledge)
            
            # Generate pledge payments
            if status != 'Cancelled' or random.random() < 0.3:  # Some cancelled pledges have payments
                payments_to_generate = installments
                
                if status == 'Active':
                    # For active pledges, only generate payments up to now
                    start_date_for_comparison = start_date.date() if isinstance(start_date, datetime) else start_date
                    elapsed_time = (current_date - start_date_for_comparison).days
                    
                    if frequency == 'Monthly':
                        periods_elapsed = elapsed_time // 30
                    elif frequency == 'Quarterly':
                        periods_elapsed = elapsed_time // 90
                    else:  # Annual
                        periods_elapsed = elapsed_time // 365
                        
                    payments_to_generate = min(periods_elapsed + 1, installments)
                
                elif status == 'Cancelled':
                    # For cancelled pledges, generate some but not all payments
                    payments_to_generate = random.randint(0, max(1, installments - 1))
                    
                for i in range(payments_to_generate):
                    if frequency == 'Monthly':
                        payment_date = start_date + timedelta(days=30 * i)
                    elif frequency == 'Quarterly':
                        payment_date = start_date + timedelta(days=90 * i)
                    else:  # Annual
                        payment_date = start_date + timedelta(days=365 * i)
                    
                    payment_status = 'Completed'
                    
                    # Last payment might be pending for active pledges
                    if status == 'Active' and i == payments_to_generate - 1 and random.random() < 0.2:
                        payment_status = 'Pending'
                    
                    payment = {
                        'payment_id': payment_id,
                        'pledge_id': pledge_id,
                        'amount': installment_amount,
                        'date': payment_date,
                        'status': payment_status
                    }
                    pledge_payments.append(payment)
                    payment_id += 1
                    
            pledge_id += 1
        
        self.pledges = pledges
        self.pledge_payments = pledge_payments
        return pd.DataFrame(pledges), pd.DataFrame(pledge_payments)

    def generate_donor_metrics(self):
        """Generate summary metrics for donors"""
        donor_metrics = []
        current_date = datetime.now().date()
        current_year = current_date.year
        
        # Calculate metrics for each constituent
        for constituent in self.constituents:
            constituent_id = constituent['constituent_id']
            
            # Get transactions for this constituent
            donor_transactions = [t for t in self.transactions 
                            if t['constituent_id'] == constituent_id]
            
            # Get pledges for this constituent
            donor_pledges = [p for p in self.pledges if p['constituent_id'] == constituent_id]
            
            # Calculate metrics
            if donor_transactions:
                # Convert all dates to the same type for comparison
                transaction_dates = []
                for t in donor_transactions:
                    t_date = t['date']
                    if isinstance(t_date, datetime):
                        transaction_dates.append(t_date.date())
                    else:
                        transaction_dates.append(t_date)
                        
                first_gift_date = min(transaction_dates)
                last_gift_date = max(transaction_dates)
                lifetime_gifts = len(donor_transactions)
                lifetime_giving = sum(t['amount'] for t in donor_transactions)
                
                # Calculate average gift
                avg_gift = lifetime_giving / lifetime_gifts if lifetime_gifts else 0
                
                # Calculate giving by year
                gifts_by_year = {}
                for t in donor_transactions:
                    year = t['date'].year if isinstance(t['date'], datetime) else t['date'].year
                    if year not in gifts_by_year:
                        gifts_by_year[year] = 0
                    gifts_by_year[year] += t['amount']
                    
                # Determine donor level
                if lifetime_giving >= 25000:
                    donor_level = 'Principal'
                elif lifetime_giving >= 5000:
                    donor_level = 'Major'
                elif lifetime_giving >= 1000:
                    donor_level = 'Mid-level'
                else:
                    donor_level = 'General'
                    
                # Determine retention status
                has_current_year_gift = False
                has_previous_year_gift = False
                
                for t in donor_transactions:
                    t_year = t['date'].year if isinstance(t['date'], datetime) else t['date'].year
                    if t_year == current_year:
                        has_current_year_gift = True
                    elif t_year == current_year - 1:
                        has_previous_year_gift = True
                
                if has_current_year_gift and has_previous_year_gift:
                    retention_status = 'Retained'
                elif has_current_year_gift and not has_previous_year_gift:
                    retention_status = 'Reactivated'
                elif not has_current_year_gift and has_previous_year_gift:
                    retention_status = 'Lapsed'
                else:
                    last_gift_year = last_gift_date.year if isinstance(last_gift_date, datetime) else last_gift_date.year
                    years_lapsed = current_year - last_gift_year
                    if years_lapsed <= 1:
                        retention_status = 'New/Recent'
                    elif years_lapsed <= 3:
                        retention_status = 'Lapsed'
                    else:
                        retention_status = 'Deeply Lapsed'
                        
                metrics = {
                    'constituent_id': constituent_id,
                    'first_gift_date': first_gift_date,
                    'last_gift_date': last_gift_date,
                    'lifetime_gifts': lifetime_gifts,
                    'lifetime_giving': lifetime_giving,
                    'average_gift': avg_gift,
                    'largest_gift': max(t['amount'] for t in donor_transactions),
                    'donor_level': donor_level,
                    'retention_status': retention_status,
                    'has_open_pledge': any(p['status'] == 'Active' for p in donor_pledges),
                    'household_id': next((h['household_id'] for h in self.households 
                                    if h['primary_constituent_id'] == constituent_id), None)
                }
                
                # Add yearly giving for analysis
                for year in range(2021, current_year + 1):
                    metrics[f'giving_{year}'] = gifts_by_year.get(year, 0)
                
                donor_metrics.append(metrics)
            
        return pd.DataFrame(donor_metrics)

    def generate_all_data(self):
        """Generate all data sets in the correct order and return them as a dictionary"""
        print("Generating funds...")
        funds_df = self.generate_funds()
        
        print("Generating constituents...")
        constituents_df = self.generate_constituents(self.num_constituents)
        
        print("Generating households...")
        households_df = self.generate_households()
                
        print("Generating campaigns...")
        campaigns_df, campaign_funds_df = self.generate_campaigns()
        
        print("Generating appeals...")
        appeals_df = self.generate_appeals()
        
        print("Generating transactions...")
        transactions_df = self.generate_transactions()
        
        print("Generating pledges...")
        pledges_df, pledge_payments_df = self.generate_pledges()
        
        # print("Generating donor metrics...")     # Uncomment these two lines if you want a table of metrics with donor acquisition and lapsed donors
        # donor_metrics_df = self.generate_donor_metrics()
        
        # Return all the dataframes in a dictionary
        return {
            'funds': funds_df,
            'constituents': constituents_df,
            'households': households_df,
            'campaigns': campaigns_df,
            'campaign_funds': campaign_funds_df,  # New table for campaign-fund mappings
            'appeals': appeals_df,
            'transactions': transactions_df,
            'pledges': pledges_df,
            'pledge_payments': pledge_payments_df,
            'donor_metrics': donor_metrics_df  # Added donor metrics table
        }


def main():
    # Initialize generator with desired configuration
    generator = NonprofitDataGenerator(
        # Basic configuration
        start_date=datetime(2021, 1, 1),        # Start of your data range
        end_date=datetime(2025, 6, 30),         # End of your data range (extended to June 2025)
        num_constituents=5000,                  # Total number of constituents to generate
        num_funds=8,                            # Number of funds to generate
        num_campaigns=20,                       # Number of campaigns to generate
        transaction_volume_multiplier=2.0,      # Multiply default transaction volumes
        organization_percentage=0.15,           # 15% of constituents are organizations
        pledge_percentage=0.12                  # 12% of donors have pledges
    )
    
    # Optional: Additional configurations (uncomment to use)
    
    # # Configure giving patterns
    # generator.configure_giving_patterns(
    #     december_weight=0.3,                  # 30% of giving happens in December
    #     giving_tuesday_weight=0.1,            # 10% of giving on Giving Tuesday
    #     appeal_response_rates={
    #         'Direct Mail': 0.15,
    #         'Email': 0.08,
    #         'Event': 0.25,
    #         'Giving Tuesday': 0.20,
    #         'Phone': 0.12
    #     }
    # )
    
    # # Configure geographic distribution
    # generator.configure_state_distribution(
    #     primary_states=['CA', 'NY', 'IL'],    # States with highest concentration
    #     secondary_states=['TX', 'FL', 'MA', 'WA', 'OR'],
    #     state_weights={
    #         'CA': 0.25, 'NY': 0.20, 'IL': 0.15,  # 60% from primary states
    #         'TX': 0.08, 'FL': 0.08, 'MA': 0.08, 'WA': 0.08, 'OR': 0.08  # 40% from secondary
    #     }
    # )
    
    # # Adjust transaction volumes
    # generator.adjust_transaction_volumes(2.5)  # Increase number of transactions by 2.5x
    
    # # Adjust constituent distribution
    # generator.adjust_constituent_distribution(
    #     org_percentage=0.20,                  # 20% organizations
    #     pledge_percentage=0.15                # 15% of donors have pledges
    # )

    # Generate all data
    data = generator.generate_all_data()

    # Save all dataframes to CSV
    print("Saving files...")
    for name, df in data.items():
        df.to_csv(f'{name}.csv', index=False)

    print("Data generation complete!")

if __name__ == "__main__":
    main()
