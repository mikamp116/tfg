import importlib
import json
import sys
import searx.engines
import searx.search


def search(search_query):
    # search_query = 'europe bans uk flights'
    # initialize engines
    searx.search.initialize()
    # load engines categories once instead of each time the function called
    engine_cs = list(searx.engines.categories.keys())
    # load module
    spec = importlib.util.spec_from_file_location(
        'utils.standalone_searx', 'searx_extra/standalone_searx.py')
    sas = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sas)
    # use function from module
    # prog_args = sas.parse_argument(['--lang [en] ', search_query], category_choices=engine_cs)
    prog_args = sas.parse_argument([search_query], category_choices=engine_cs)
    search_q = sas.get_search_query(prog_args, engine_categories=engine_cs)
    res_dict = sas.to_dict(search_q)
    # sys.stdout.write(json.dumps(
    #     res_dict, sort_keys=True, indent=4, ensure_ascii=False,
    #     default=sas.json_serial))
    # res = json.dumps(res_dict, sort_keys=True, indent=4, ensure_ascii=False, default=sas.json_serial)
    return res_dict['results']


if __name__ == '__main__':
    query = 'europe bans uk flights'
    response = search(query)
    print(response)
