from collections import defaultdict
class MTParser:
    def __init__(self,frequent_terms,tkn_concept_map,concept_score_map):
        self.frequent_terms = frequent_terms
        self.tkn_concept_map = tkn_concept_map
        self.concept_score_map = concept_score_map
        # self.tkn_noun_score_map = tkn_noun_score_map

    def combine_scores(self, tkn_concept_map, concept_score_map, mts_in_consideration):
        mt_scores_map = {}
        for i in mts_in_consideration:
            # mt_score = mt_scores_map.get(i,0.0)#0.0
            mt_score = 0.0#tkn_noun_score_map.get(i, 0.0)  # 0.0
            if i in tkn_concept_map:
                for k in tkn_concept_map[i]:  #####add scors for all concepts of partitcular mt
                    mt_score += concept_score_map[k]
            mt_scores_map[i] = mt_score
        return mt_scores_map
    def get_mts_scorewise(self,lst_of_mts,n_max_pred_mts,mt_confidence ):

        mt_class = mt_confidence
        if mt_class == 3:
            mts_in_consideration = self.frequent_terms['score3_dynamicMTs']
        elif mt_class == 2:
            mts_in_consideration = self.frequent_terms['score2_dynamicMTs']
        if len(mts_in_consideration) <= n_max_pred_mts:
            lst_of_mts[mt_class] = mts_in_consideration
        else:
            # lst_of_mts.append((2, frequent_terms['mts2']))
            # tmp.extend(frequent_terms['mts2'])
            # mt_scores_map = self.combine_scores(self.tkn_noun_score_map, self.tkn_concept_map,
            #                                self.concept_score_map,
            #                                mts_in_consideration)
            mt_scores_map = self.combine_scores( self.tkn_concept_map,
                                                self.concept_score_map,
                                                mts_in_consideration)
            max_score = max(mt_scores_map.values())
            max_score_mts = [k for k, v in mt_scores_map.items() if v == max_score]
            if len(max_score_mts) <= n_max_pred_mts:
                lst_of_mts[mt_class] = max_score_mts
            else:
                # lst_of_mts[mt_class] = ['TIE-BRAKE',*max_score_mts]
                return []
                pass #todo edit later tiebraker

        return lst_of_mts
    def get_mts(self,lst_of_mts,n_max_pred_mts,mt_confidence ):
        new_mts =[]
        mt_class = mt_confidence
        if mt_class == 3:
            mts_in_consideration = self.frequent_terms['score3_dynamicMTs']
        elif mt_class == 2:
            mts_in_consideration = self.frequent_terms['score2_dynamicMTs']
        if len(mts_in_consideration) <= n_max_pred_mts:
            # lst_of_mts.extend( mts_in_consideration)
            new_mts.extend( mts_in_consideration)

        else:
            # lst_of_mts.append((2, frequent_terms['mts2']))
            # tmp.extend(frequent_terms['mts2'])
            mt_scores_map = self.combine_scores( self.tkn_concept_map,
                                           self.concept_score_map,
                                           mts_in_consideration)
            max_score = max(mt_scores_map.values())
            max_score_mts = [k for k, v in mt_scores_map.items() if v == max_score]
            if len(max_score_mts) <= n_max_pred_mts:
                # lst_of_mts.extend( max_score_mts)
                new_mts.extend( max_score_mts)
            else:
                # raise NotImplementedError('')
                return []

                # lst_of_mts[mt_class] = ['TIE-BRAKE',*max_score_mts]
                pass #todo edit later tiebraker

        # return lst_of_mts
        return new_mts

    def update_maps(self,lst_of_mts):
        if lst_of_mts:
            self.tkn_concept_map = {g: v for g, v in self.tkn_concept_map.items() if g not in lst_of_mts}

            # self.tkn_noun_score_map = {k: v for k, v in self.tkn_noun_score_map.items() if
            #                   k not in lst_of_mts}  ####need to check mt1 , and not temp here

    def get_tkn_noun_score_map(self):
        return self.tkn_noun_score_map

    def get_tkn_concept_map(self):
        return self.tkn_concept_map

    def get_max_freq_token(self,tkn_concept_map):
        freq_tkns = defaultdict(list)
        for m, n in tkn_concept_map.items():
            # nt= [r for r in nt if r !='item']
            # freq_tkns[m] = len(nt)
            freq_tkns[m] = len(n)
        # tkn_with_max_concepts = max(freq_tkns, key=freq_tkns.get)   #dont use , will return only one max key , even if u have two keys woith same max
        temp2 = max(freq_tkns.values())
        tkn_with_max_concepts = [b for b, n in freq_tkns.items() if n == temp2]
        return tkn_with_max_concepts

