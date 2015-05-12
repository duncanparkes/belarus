import re

import requests
import lxml.html

import scraperwiki

resp = requests.get('http://house.gov.by/index.php/,7508,,,,1,,,0.html')
root = lxml.html.fromstring(resp.text)

trs = root.xpath("//tr[td[a[@class='d_list']]]")

data = []

for tr in trs:
    member = {'chamber': 'House of Representatives'}
    member['name'] = tr.xpath('.//a')[0].text_content().strip()
    member['details_url'] = tr.xpath('.//a')[0].get('href')
    member['constituency'] = tr.xpath('td')[-1].text_content().strip()
    member['constituency_id'] = int(re.search('\d+', member['constituency']).group())

    member_resp = requests.get(member['details_url'])
    member_root = lxml.html.fromstring(member_resp.text)

    email_texts = member_root.xpath("//p[contains(., 'E-mail')]")

    if len(email_texts) > 1:
        print "Lots of emails!"
        import pdb;pdb.set_trace()
    elif len(email_texts) == 1:
        email_text = email_texts[0].text_content().strip()

        if email_text == 'E-mail:':
            print "No email"
        elif email_text.startswith('E-mail:'):
            member['email'] = email_text[7:].strip()
        else:
            print "Bad email"
    else:
        print "No email"

        # A couple of people have the following instead of 'E-mail:'
        # E-ma\xb3l:

    data.append(member)
    scraperwiki.sqlite.save(unique_keys=['constituency_id'], data=data)


print "Missing constituency ids: " + repr(set(range(1, 111)) - set([x['constituency_id'] for x in data]))






# # Find something on the page using css selectors
# root = lxml.html.fromstring(html)
# root.cssselect("div[align='left']")
#
# # Write out to the sqlite database using scraperwiki library

# # An arbitrary query against the database
# scraperwiki.sql.select("* from data where 'name'='peter'")

# You don't have to do things with the ScraperWiki and lxml libraries.
# You can use whatever libraries you want: https://morph.io/documentation/python
# All that matters is that your final data is written to an SQLite database
# called "data.sqlite" in the current working directory which has at least a table
# called "data".
