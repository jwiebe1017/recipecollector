"""
class Recipes module
contains the Recipes class which:
 - given url, with ld+json google standardized formatting
 - can parse and interpret instructions/ingredients
 - multiply the ingredients for different portion sizes
"""
import logging
import re
from decimal import Decimal
from fractions import Fraction

import requests
import json
from bs4 import BeautifulSoup as bs
from utils.utils import logging_setup

__author__ = 'jwiebe1017'
__version__ = '1.0.0'
__credits__ = ['stackoverflow', 'me, myself, and I', 'you I guess?']

log = logging_setup(__name__, False)


class Recipes:
    def __init__(self, url: str):
        self.site = url
        self.site_success: bool = False
        self.ld_json_present: bool = False
        self.ingredients: list = list()
        self.instructions: list = list()
        self.original_ingredients: list = list()

    @staticmethod
    def _parse_instructions(ins_dict: dict):
        try:
            return list(
            map(
                lambda inst:
                str(inst[0]) + ': ' + inst[1]['text'],
                enumerate(ins_dict)
            )
        )
        except KeyError:
            logging.error('This sites structure is odd')
            return ins_dict

    def collect_recipe_from_url(self):
        req = requests.get(self.site)
        if req.status_code == 200 and req.content is not None:
            log.info('successful site')
            self.site_success = True
            try:
                meta_json = json.loads(  # convert bs javascript section to usable json format
                    str(
                        bs(
                            req.content,
                            'html.parser'
                        ).find(
                            "script",
                            {
                                "type": "application/ld+json"
                            }
                        ).contents[0]
                    )
                )
            except AttributeError:
                log.error('LD + JSON not Present, sorry.')
                return 'ld + json not present'

            if meta_json and isinstance(meta_json, dict):
                self.ld_json_present = True
                log.info('ld+json present, attempting to parse...')
                try:
                    self.ingredients = meta_json['recipeIngredient']
                    self.instructions = self._parse_instructions(meta_json['recipeInstructions'])

                except KeyError:
                    recipe = next(
                        filter(  # grab only appropriate sections per Google's build suggestions
                            None,
                            [x if x['@type'] == 'Recipe' else None for x in meta_json['@graph']]

                        )
                    )
                    self.ingredients = recipe['recipeIngredient']
                    self.instructions = self._parse_instructions(recipe['recipeInstructions'])

            elif meta_json and isinstance(meta_json, list):
                self.ld_json_present = True
                try:
                    self.ingredients = meta_json[0]['recipeIngredient']
                    self.instructions = self._parse_instructions(meta_json[0]['recipeInstructions'])

                except KeyError:
                    recipe = next(
                        filter(  # grab only appropriate sections per Google's build suggestions
                            None,
                            [x if x['@type'] == 'Recipe' else None for x in meta_json[0]['@graph']]

                        )
                    )
                    self.ingredients = recipe['recipeIngredient']
                    self.instructions = self._parse_instructions(recipe['recipeInstructions'])

    def multiply_recipe(self, by: int = 1):
        if self.ingredients:
            self.original_ingredients = self.ingredients
            split_ing = tuple(
                map(
                    lambda x:
                    re.sub(  # find and group split-nums for eval
                        r'(\d+)\s+(\d)/(\d)',
                        r'\1+\2/\3',
                        x
                        # isolate ingredient numbers for eval
                    ).partition(' '),
                    self.ingredients
                )
            )

            new_ing = map(
                lambda ing:
                Fraction(
                    Decimal(
                        str(
                            round(
                                eval(
                                    ing[0]
                                ) * by,
                                2
                            )
                        )
                    )
                ).limit_denominator(
                    10
                ).__str__(),
                split_ing
            )

            self.ingredients = list(
                map(
                    lambda zip_ings:
                    zip_ings[0] + ' ' + zip_ings[1][-1],
                    zip(new_ing, split_ing)
                )
            )
        else:
            raise 'NotImplemented: please add ingredients'
