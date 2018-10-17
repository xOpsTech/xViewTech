import requests
from bs4 import BeautifulSoup
import constants
import templates
import ES_Reader as ES
import logging

logger = logging.getLogger(__name__)

# print soup.prettify()

HAPPY_STATE = 'service is operating normally'
INFORMATIONAL_STATE = 'informational message'
DEGRADATIONAL_STATE = 'service degradation'
DISRUPTIONAL_STATE = 'service disruption'

status_dict = {
    HAPPY_STATE: constants.STATUS_GOOD,
    DEGRADATIONAL_STATE: constants.STATUS_WARNING,
    DISRUPTIONAL_STATE: constants.STATUS_CRITICAL
}

html_tags = [
    ('div', {"id": 'NA_block'}),
    ('div', {"id": 'SA_block'}),
    ('div', {"id": 'EU_block'}),
    ('div', {"id": 'AP_block'})
]


def run():
    page = requests.get(constants.URL_AWS)
    soup = BeautifulSoup(page.content, 'html.parser')

    json_template = templates.get_json_template()
    json_template.update({
        'source': constants.SOURCE_AWS,
        'sourceUrl': constants.URL_AWS,
        'sourceStatus': constants.STATUS_GOOD,
    })

    try:
        service_status = constants.STATUS_GOOD
        status_set = set()

        for html_tag in html_tags:
            html_element = soup.find(html_tag[0], html_tag[1])
            html_tables = html_element.find_all('table', attrs={'class': 'fullWidth'})

            if len(html_tables) == 2:
                table = html_tables[1]
                table_body = table.find('tbody')

                rows = table_body.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    service_name = cols[1].text.strip()
                    service_value = cols[2].text.strip()
                    # if service_value.lower() in [DEGRADATIONAL_STATE, DISTRUPTIONAL_STATE]:
                    #     service_status = constants.STATUS_CRITICAL
                    status_set.add(status_dict.get(service_value.lower()))
                    
                    json_template['services'].append({
                        'name': service_name,
                        'value': service_value
                    })

        if constants.STATUS_CRITICAL in status_set:
            service_status = constants.STATUS_CRITICAL
        elif constants.STATUS_WARNING in status_set:
            service_status = constants.STATUS_WARNING
        json_template['sourceStatus'] = service_status

        # print json.dumps(json_template)
        ES.create_index_data(json_template)
    except Exception:
        logger.error('error parsing %s', constants.SOURCE_AWS, exc_info=1)
        logger.error("-" * 100)
        logger.error(unicode(soup))
        logger.error("-" * 100)
        json_template['sourceStatus'] = constants.STATUS_CRITICAL
        ES.create_index_data(json_template)


if __name__ == '__main__':
    run()
