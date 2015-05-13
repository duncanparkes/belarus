import re
from urlparse import urljoin, urlsplit

import requests
import lxml.html

import scraperwiki

en_source_house_of_representatives = 'http://house.gov.by/index.php/,7508,,,,1,,,0.html'
resp = requests.get(en_source_house_of_representatives)
root = lxml.html.fromstring(resp.text)

trs = root.xpath("//tr[td[a[@class='d_list']]]")

data = []

for tr in trs:
    member = {'chamber': 'House of Representatives'}

    # For now, we'll just set the party to blank.
    member['party'] = u''

    member['name'] = tr.xpath('.//a')[0].text_content().strip()
    member['details_url'] = tr.xpath('.//a')[0].get('href')
    member['id'] = int(urlsplit(member['details_url']).path.split(',')[2])

    member['constituency'] = tr.xpath('td')[-1].text_content().strip()
    member['constituency_id'] = int(re.search('\d+', member['constituency']).group())

    member_resp = requests.get(member['details_url'])
    member_root = lxml.html.fromstring(member_resp.text)

    member['image'] = urljoin(
        en_source_house_of_representatives,
        member_root.xpath('//h1')[0].getnext().xpath('.//img')[0].get('src')
        )

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
