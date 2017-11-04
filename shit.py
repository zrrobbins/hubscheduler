
API_KEY = '723d4607077a2565f61ea4e2b790'



# Compute the timedelta between two date strings in ISO format
def compute_day_delta(date_A, date_B):
    date_A = datetime.strptime(date_A, "%Y-%m-%d")
    date_B = datetime.strptime(date_B, "%Y-%m-%d")
    return abs((date_B - date_A).days)

# Fetch all partners
response = requests.get('https://candidate.hubteam.com/candidateTest/v1/partners', params={'userKey':API_KEY})

json_data = json.loads(response.content.decode())
# Make list of partners
#partners = sample_data['partners']
partners = json_data['partners']

# Make two dicts:
#   partner_dict will map partner information to their email
#   country_dict will map partners to their country
partner_dict = {}
country_dict = {}
for partner in partners:
    partner_dict[partner['email']] = partner
    if partner['country'] in country_dict.keys():
        country_dict[partner['country']].append(partner['email'])
    else:
        country_dict[partner['country']] = [partner['email'], ]

# TODO: remove debug print
#pprint(partner_dict)
#pprint(country_dict)

# This is the json object we will POST to the API
response_json_object = {"countries": []}

# For a list of partners in a country, find consecutive date tuples (possible event dates) that work for each partner
# in that country. Return a list of possible event dates.
def find_event_dates(partners_in_country):
    possible_event_dates = {}

    for ptnr in partners_in_country:
        last_date = None
        # For each date in the partner's available dates
        for date in partner_dict[ptnr]['availableDates']:
            # Check to see if we found two consecutive dates
            if last_date is not None and compute_day_delta(last_date, date) == 1:
                # If we haven't found this tuple before, create a new tuple in the dict representing this date pair
                # with the email of the partner, otherwise add email to the bucket of the dict for this date tuple
                if (last_date, date) not in possible_event_dates:
                    possible_event_dates[(last_date, date)] = [ptnr, ]
                else:
                    possible_event_dates[(last_date, date)].append(ptnr)
            last_date = date

    return possible_event_dates


# For each country
for country in country_dict.keys():

    # Find possible event dates (consecutive dates represented as tuples) for partners in this country
    country_date_tuples = find_event_dates(country_dict[country])

    # If at least one date tuple works where 1 partner can make it
    if len(country_date_tuples) > 0:
        # Sort keys by earliest event date first
        sorted_keys = sorted(country_date_tuples.keys(), key = lambda x: datetime.strptime(x[0], "%Y-%m-%d"))
        for k, v in country_date_tuples.items():
            print(k, len(v))
        print(sorted_keys)
        #sorted_keys = sorted(country_date_tuples.keys(), reverse=True)
        max_key = max(country_date_tuples, key=lambda x: len(set(country_date_tuples[x])))
        max_key_val = len(country_date_tuples[max_key])
        print('max key val = {}'.format(max_key_val))

        # Pick the earliest event date with this max key value
        best_event_date = None
        for date_tuple in sorted_keys:
            print(date_tuple)
            if len(country_date_tuples[date_tuple]) == max_key_val:
                best_event_date = date_tuple[0]
                break

        print('best_event_date: {}'.format(best_event_date))
        # Grab the date tuple that has the most possible attendees for the country!

        # TODO: remove debug print
        #print('country = {}, maxkey = {}, maxkey length = {}'.format(country, max_key, len(country_date_tuples[max_key])))
        print('country = {}, best_date = {}, length = {}\n\n'.format(country, best_event_date, len(country_date_tuples[max_key])))
        country_info = {
            "attendeeCount" : len(country_date_tuples[max_key]),
            "attendees": country_date_tuples[max_key],
            "name": country,
            "startDate": best_event_date
        }
    else:
        country_info = {
            "attendeeCount": 0,
            "attendees": [],
            "name": country,
            "startDate": None
        }

    # Add country info to response json
    response_json_object['countries'].append(country_info)

pprint(response_json_object)
response = requests.post(
    'https://candidate.hubteam.com/candidateTest/v1/results',
    params={'userKey':API_KEY},
    json=response_json_object
)

# Print response data
print(response.status_code)
pprint(json.loads(response.content.decode()))
