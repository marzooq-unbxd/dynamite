import ast
from collections import defaultdict
import requests
import os
import logging
from flask import Flask, request, jsonify
from utils.parser import MTParser
import config
from nltk import WordNetLemmatizer


app = Flask(__name__)
import json
with open('dynamic_mts/mts_concepts.json')as f:
    dynamic_mts = json.load(f)
lmtzr  = WordNetLemmatizer()


# import nltk
# from nltk.corpus import stopwords
# set(stopwords.words('english'))
stopwords = ['a', 'an', 'the', 'and', 'it', 'for', 'or', 'but', 'in', 'my', 'your', 'our', 'and' 'their','by']
# concept_score_map = {'item': 0.5983606557377049, 'material': 0.1775619906363794, 'tool': 0.13175591531755915, 'product': 0.18493150684931506, 'equipment': 0.29539866526167896, 'accessory': 0.23376049491825013, 'hand tool': 0.06164383561643835, 'device': 0.08058017727639001, 'appliance': 0.1053740779768177, 'component': 0.05593607305936074, 'amenity': 0.0380517503805175, 'container': 0.0839041095890411, 'power tool': 0.048923679060665366, 'structure': 0.07045009784735812, 'facility': 0.03131115459882583, 'protective clothing': 0.043835616438356165}
concept_score_map = {'item': 0.5983606557377049, 'material': 0.4050632911392405, 'equipment': 0.7435897435897436, 'product': 0.5, 'tool': 0.41818181818181815, 'accessory': 0.7419354838709677, 'appliance': 0.7692307692307693, 'device': 0.5882352941176471, 'hand tool': 0.5, 'container': 0.875, 'component': 0.5833333333333334, 'structure': 0.8571428571428571, 'amenity': 0.5555555555555556, 'power tool': 0.7142857142857143, 'facility': 0.5714285714285714, 'protective clothing': 0.8}

logger = logging.getLogger(__name__)



# ASTERIX_API = "{}/cores/{}/analyzers/mw?query={}&format=raw"
# ASTERIX_API = "{}/v2/cores/{}/analyzers/search?query={}&format=raw"   #analysed query but no distinction betweeen mts etc
ASTERIX_API = "{}/v2/cores/{}/analyzers/search"   #analysed query but no distinction betweeen mts etc
# ASTERIX_API = "{}/v2/cores/{}/analyzers/search/assets?query={}&format=raw" #no analysed query

config_manager = None

list_of_allowed_concepts=['item', 'material', 'tool', 'product', 'equipment', 'accessory', 'hand tool', 'device', 'appliance', 'component', 'amenity', 'container', 'power tool', 'structure', 'facility', 'protective clothing']




@app.route("/")
def home():
    return " Ahoi. You have summoned the service for  analyzed query with dynamic mts!"


def init():
    pass
    #active_sites_to_load = list(config.ACTIVE_SITE_CONFIG.keys())
    #_ = load_statistical_data(config.AWS_ACCESS_KEY_ID, config.AWS_SECRET_ACCESS_KEY, active_sites_to_load,"live")



def clean_textv2( text, isite_name):
    try:
        # url = config.ASTERIX_URL.rstrip("/")
        # response = requests.get(url)
        # print(response.text)

        url = ASTERIX_API.format(config.ASTERIX_URL.rstrip("/"), isite_name)
        response = requests.get(url,params={'query': text,"format":"raw"})

        # response = "{'analyzedQuery': 'N95 Particulate Respirator<><%><##>mask Pack 20'}"
        # response = "{'analyzedQuery': 'Tridon +Cable<><%><##>lead Ties 150 x 4mm Black'}"
        # response = requests.get(url,params={'query': text,"format":"raw"})

        # response = requests.get(url,params={'query': text})
        if response.status_code == 200:
            # return response.text
            # return response.json()#['analyzedQuery']
            parsed_json = ast.literal_eval(response.text)
            # parsed_json = ast.literal_eval(response)

            # parsed_json = ast.literal_eval(json.dumps(response.text))

            return parsed_json#['analyzedQuery']


        else:
            logger.error("response  status: {} url: {}".format( response.status_code, url))
            return {'analyzedQuery':text}
    except Exception as e:
        logger.error("clean_text excep {}".format( str(e)))
        return {'analyzedQuery':text}

def get_mandatory_terms(original_query, q_ans):
    data = []  # defaultdict(1.0)

    if 'data' in q_ans:
        hi = q_ans['data']
        if original_query in hi:
            hii = hi[original_query]
            if 'mandatoryTerms' in hii:
                x = hii['mandatoryTerms']
                for i in x:
                    data.append(i)

    return data
def get_mandatory_termsv2(original_query, q_ans):
    analysed_query_mts = []

    try:
        q_ans = q_ans['analyzedQuery']
        for i in q_ans.split():
            if i[0]=='+':
                analysed_query_mts.append(i)
    except:
                 #dont write pass , analyzed query might not even be present
            logger.error("analyzed query absent in dictionary {}".format(q_ans))

    return analysed_query_mts
import re
def add_dynamic_mts_to_analyzed_query(analyzed_query, query_dynamic_mts):

    analyzed_query=analyzed_query['analyzedQuery']
    analyzed_query_tkns = analyzed_query.split()

    for i in query_dynamic_mts:
        pos_dynamic_mt = [x for x in analyzed_query_tkns if i ==x.lower() or x.lower().startswith(str(i)+'<')]
        if len(pos_dynamic_mt)>1:
            continue
        else:
            analyzed_query_tkns = ['+' + x if x.lower()==i else x for x in analyzed_query_tkns]

    return {'analyzedQuery':" ".join(analyzed_query_tkns)}


def basic_clean(k):
    # if not k:
    #     return None

    k= ''.join(ch for ch in k if ch.isalpha())

    # if all(not str.isalpha(charac) for charac in k):   #not all digits
    # if any(not str.isalpha(charac) for charac in k):   #any digit ignore
    #     return None
    # else:
    #     k = k.replace(",", "")
    #     k = k.replace(".", "")
    return k.lower()

def get_inverse_map(tkn_concept_map):
    concept_tkn_map = defaultdict(list)
    for p in tkn_concept_map:
        for q in tkn_concept_map[p]:
            concept_tkn_map[q].extend([p])
    return concept_tkn_map
def get_original_tokens (lst_of_mts,orig_opt_tk):
    orig_lst_of_mts = [j for j, k in orig_opt_tk.items() if k in lst_of_mts]
    return orig_lst_of_mts
def get_predicted_mts(act_mt,original_query):

    act_mt = act_mt
    tokens = original_query.split()
    act_mt = [t.lower() for t in act_mt if t] #x.actual_mts
    query_tkns = [t.lower() for t in tokens]
    query_tkns = [t for t in query_tkns if t not in stopwords ]    ###########should only be tokens withich are not top words->to genrate max mt threshold

    # query_tkns = [t for t in query_tkns if len(t)!=1 ]    ###########todo change later ->removing one letter tokens
    query_tkns = [t for t in query_tkns if not (len(t)==1 and t.isalpha())]    ###########todo change later ->removing one letter tokens

    # opt_tk = [x for x in query_tkns if x not in act_mt and ( or )]   #hot-fix,,,token might not bre present in original-cleanedd----doing so to avoid tokens like 'no' coming up '



    ########len of query ===== len of query cleaned of stopwords etc NEWWWWW

    opt_tk=[]
    for tkn in query_tkns:
        # if tkn not in original_cleaned_hashmap:
            if tkn not in act_mt:
                #todo editing 10 may if not (any(x.isdigit() for x in tkn))  :  #another hadk 20mm has a concept, hence avoiding any numbered token
                    opt_tk.append(tkn)                      #40w e27 45mm round , probase able to identify e27 , will not be able to identify anymore

    ######was lemmatizing earliier and comparing, but act mts already stemmed, need to compare stemmed and then lemmatize orginal
    orig_opt_tk = {x:lmtzr.lemmatize(basic_clean(x)) for x in opt_tk}   ###'cantilever clean


    opt_tk = [lmtzr.lemmatize(basic_clean(x)) for x in opt_tk]   ###'cantilever clean

    opt_tk = [x for x in opt_tk if x]  ###'' might come up


    if len(query_tkns)==3 or len(query_tkns)==4 or len(query_tkns)==5:
        n_max_pred_mts = 1
    if len(query_tkns)>=6:
        n_max_pred_mts = 2
    # if len(opt_tk)<=2:
    #     return None
    if len(query_tkns)<=2:
        return None

    n_max_pred_mts = n_max_pred_mts - len(act_mt)

    if n_max_pred_mts <=0:
        return None#"Max limit mts reached"


    def check_if_in_frequent_terms(x):
        first_stage_inf = defaultdict(list)
        for term in x:
            if term in dynamic_mts['score3_dynamicMTs']:
                first_stage_inf['score3_dynamicMTs'].extend([term])
                term_concepts = dynamic_mts['score3_dynamicMTs'][term]
                tkn_concept_map[term]=term_concepts
            elif term in dynamic_mts['score2_dynamicMTs']:
                first_stage_inf['score2_dynamicMTs'].extend([term])
                term_concepts = dynamic_mts['score2_dynamicMTs'][term]
                tkn_concept_map[term]=term_concepts
        return dict(first_stage_inf),tkn_concept_map
    tkn_concept_map = {}

    frequent_terms, tkn_concept_map =check_if_in_frequent_terms(opt_tk)

    tmp=[]    #list_of_mts_predicted  by us

    ##################todo considering concepts only for tokens with lesser score

    tkn_concept_map = {g: v for g, v in tkn_concept_map.items() if
                       g not in tmp}                                    ####IMP...first stage tokens should not be considered
    lst_of_mts = []
    mtp=MTParser(frequent_terms,tkn_concept_map,concept_score_map)
    if frequent_terms:     ###assuming that mts1 and mts2 will not have same term appearing
        new_mts = []
        if 'score3_dynamicMTs' in frequent_terms:

            new_mts = mtp.get_mts(lst_of_mts, n_max_pred_mts, mt_confidence=3)
            lst_of_mts.extend(new_mts)
            # n_max_pred_mts = n_max_pred_mts - len(lst_of_mts.get(3,0))                ##only adding here->>since it goes down
            n_max_pred_mts = n_max_pred_mts - len(new_mts)                ##only adding here->>since it goes down


        if n_max_pred_mts<=0:
            # return lst_of_mts
            return get_original_tokens(lst_of_mts, orig_opt_tk)

        ##################todo update map

        # mtp.update_maps(lst_of_mts.get(3,None))
        mtp.update_maps(new_mts)
        new_mts=[]
        if 'score2_dynamicMTs' in frequent_terms:
            new_mts = mtp.get_mts(lst_of_mts, n_max_pred_mts,mt_confidence=2)
            # lst_of_mts = mtp.get_mts(lst_of_mts, n_max_pred_mts,mt_confidence=2)
            lst_of_mts.extend(new_mts)
            n_max_pred_mts = n_max_pred_mts - len(new_mts)                ##only adding here->>since it goes down

        if n_max_pred_mts <= 0:
            # return lst_of_mts
            return get_original_tokens(lst_of_mts, orig_opt_tk)

        # mtp.update_maps(lst_of_mts.get(2,None))

    # return lst_of_mts  ###this will contain lemmatized tokens
    return get_original_tokens(lst_of_mts, orig_opt_tk)



# def get_statistical_helper(requestId, site, query, did=None, model='statistical'):
def get_statistical_helper( site, query, ):

    # cleaned_query = clean_text(requestId, query, site)
    analyzed_query = clean_textv2( query, site)

    if site != 'www-mitre10new-co-nz805201575257125':
        return jsonify(analyzed_query)
    # print("analyzedQuery",type(analyzed_query))
    current_mts = get_mandatory_termsv2(query,analyzed_query) #query ->>org query . query_assets ->mts,syns etc
    # print("current_mts",current_mts)
    query_dynamic_mts = get_predicted_mts(current_mts,query)
    if not query_dynamic_mts:
        return jsonify(analyzed_query)
    else :
        return jsonify(add_dynamic_mts_to_analyzed_query( analyzed_query, query_dynamic_mts))
    return jsonify({"message": "query not found"})


@app.route("/v2/cores/<site>/analyzers/search" ,methods=['GET'])
def get_statistical_categoryv2(site):
    # data = request.get_json()
    # requestId = request.headers.get('unbxd-request-id')
    query = request.args.get('query')
    # model = request.args.get('model')
    # deploymentId = request.args.get('deployment')
    if query is None:
        return jsonify({"message": "Error: {}".format("No query")}), 400
    response = jsonify({"message": "query not found"})
    try:
        response = get_statistical_helper(site, query)
    except Exception as e:
        logger.error(
            "Error while fetching predicted mts  for site: {}, query: {}, error: {}".format (site, query, str(e)))
        response = jsonify({"message": "Error: {}".format(str(e))})
        return response, 500
    return response
