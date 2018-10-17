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
    ('table', {'data-zone-name':'americas'}, {'class': 'status-table region-status-table default active'}),
    ('table', {'data-zone-name':'europe'}, {'class': 'status-table region-status-table'}),
    ('table', {'data-zone-name':'asia'}, {'class': 'status-table region-status-table'}),
    ('table', {'data-zone-name':'azure-government'}, {'class': 'status-table region-status-table'}),
]


def run():
    page = requests.get(constants.URL_AZURE)
    soup = BeautifulSoup(page.content, 'html.parser')

    json_template = templates.get_json_template()
    json_template.update({
        'source': constants.SOURCE_AZURE,
        'sourceUrl': constants.URL_AZURE,
        'sourceStatus': constants.STATUS_GOOD,
    })

    try:
        service_status = constants.STATUS_GOOD
        status_set = set()

        html_element = soup.find('div', attrs={"class":"section section-size2 status status-information"})
        html_row = html_element.find('div', attrs={'class':'row row-size2 column status-content'})
        for html_tag in html_tags:
            html_tables = html_row.find_all(html_tag[0], html_tag[1])
            if len(html_tables) == 2:
                table = html_tables[1]
                table_body = table.find('tbody')
                rows = table_body.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols)>2:
                        service_name = cols[0].text.strip()
                        status_cols = row.find_all('td', attrs={'class':'status-cell'})
                        service_values = []
                        for status_col in status_cols:
                            service_value = status_col.text.strip()
                            # if service_value.lower() in [DEGRADATIONAL_STATE, DISTRUPTIONAL_STATE]:
                            #     service_status = constants.STATUS_CRITICAL
                            service_values.append(service_value.lower())
                        status_set.update(service_values)

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
