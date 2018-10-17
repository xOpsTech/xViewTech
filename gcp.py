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


def run():
    page = requests.get(constants.URL_GOOGLE)
    soup = BeautifulSoup(page.content, 'html.parser')

    json_template = templates.get_json_template()
    json_template.update({
        'source': constants.SOURCE_GOOGLE,
        'sourceUrl': constants.URL_GOOGLE,
        'sourceStatus': constants.STATUS_GOOD,
    })

    try:
        service_status = constants.STATUS_GOOD
        status_set = set()


        html_element = soup.body.find('div', attrs={'class':'body'})
        html_main = html_element.find('div', attrs={'id':'maia-main'})
        html_timeline = html_element.find('div', attrs={'class':'timeline clearfix'})
        html_table = html_timeline.find('table')
        #--------------------------------------
        #Check this line below and above this
        #-------------------------------------
        #table_body = html_tables.find('tbody')

        rows = html_table.find_all('tr')
        #print(rows)
        for row in rows[1:-1]:
            service_name_column = row.find('td', attrs={'class':'service-status'})
            service_status_column = row.find('td', attrs={'class':'day col8'})
            service_name = service_name_column.text.strip()
            service_status = service_status_column.span['class'][2]

            if service_status.lower()=='high':
                status_set.add(constants.STATUS_CRITICAL)
            elif service_status.lower()=='medium':
                status_set.add(constants.STATUS_WARNING)
            else:
                status_set.add(constants.STATUS_GOOD)


            json_template['services'].append({
                'name': service_name,
                'value': service_status
            })

        if constants.STATUS_CRITICAL in status_set:
            service_status = constants.STATUS_CRITICAL
        elif constants.STATUS_WARNING in status_set:
            service_status = constants.STATUS_WARNING
        json_template['sourceStatus'] = service_status

        #print(json_template)
        ES.create_index_data(json_template)
    except Exception:
        logger.error('error parsing %s', constants.SOURCE_GOOGLE, exc_info=1)
        logger.error("-" * 100)
        logger.error(unicode(soup))
        logger.error("-" * 100)
        json_template['sourceStatus'] = constants.STATUS_CRITICAL
        ES.create_index_data(json_template)


if __name__ == '__main__':
    run()
