from utils.utils import logging_setup
from utils.recipe import Recipes

__author__ = 'jwiebe1017'
__version__ = '1.0.0'
__credits__ = ['stackoverflow', 'me, myself, and I', 'you I guess?']


def main():
    log = logging_setup(__name__, False)
    url = input('Enter Site:')
    log.info('Thanks, setting things up...')
    recipe = Recipes(url)
    recipe.collect_recipe_from_url()
    print(r'Final Results:')
    print('INGREDIENTS:\n\n' + '\n'.join(recipe.ingredients))
    print('\nINSTRUCTIONS:\n\n' + '\n'.join(recipe.instructions))
    portion_q = input('Change Portion Size? (y/n)')
    if portion_q == 'y':
        by = input('Sweet, by how much? Ints only please.')
        recipe.multiply_recipe(int(by))
        print(r'Final Results:')
        print('INGREDIENTS:\n\n' + '\n'.join(recipe.ingredients))
        print('\nINSTRUCTIONS:\n\n' + '\n'.join(recipe.instructions))


if __name__ == '__main__':
    main()
