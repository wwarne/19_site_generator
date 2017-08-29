import argparse
import logging
import os
import markdown
import json
import shutil
from collections import OrderedDict
from jinja2 import Environment, FileSystemLoader
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.smarty import SmartyExtension
from livereload import Server

logging.basicConfig(level=logging.ERROR)
ARTICLES_PATH = 'articles'
HTML_PATH = 'website'


def load_file(filepath):
    try:
        with open(filepath, mode='r', encoding='utf-8') as f:
            return f.read()
    except OSError:
        return None


def save_file(filepath, data_to_write):
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, mode='w', encoding='utf-8') as f:
            f.write(data_to_write)
    except OSError as e:
        logging.error('Can\'t save data to {}. Error: {}'.format(filepath, e))
        return
    logging.info('Successfully save data to {}'.format(filepath))


def get_filename_without_extension(filepath):
    _, filename = os.path.split(filepath)
    name, _ = os.path.splitext(filename)
    return name


def get_page_href(page_source_path, page_topic_slug):
    filename = get_filename_without_extension(page_source_path) + '.html'
    return ''.join((page_topic_slug, '/', filename))


def get_saving_file_path(source_path, topic_slug):
    filename = get_filename_without_extension(source_path) + '.html'
    return os.path.join(HTML_PATH, topic_slug, filename)


def render(template_name, context):
    env = Environment(loader=FileSystemLoader('./templates'))
    template = env.get_template(template_name)
    return template.render(**context)


def make_indexes(config):
    topics = {e['slug']: e['title'] for e in config['topics']}
    categories = split_articles_to_categories(config)
    make_main_index(topics, categories)
    make_sub_indexes(topics, categories)


def make_main_index(topics, categories):
    data_to_template = {
        'topic_names': topics,
        'articles': categories
    }
    index_html = render('main_index.html', data_to_template)
    main_index_path = get_saving_file_path(source_path='index.html', topic_slug='')
    save_file(filepath=main_index_path, data_to_write=index_html)


def make_sub_indexes(topics, categories):
    for section_name, section_articles in categories.items():
        data_to_template = {
            'section_name': topics[section_name],
            'articles': section_articles
        }
        sub_index_html = render('category_index.html', data_to_template)
        sub_index_path = get_saving_file_path(source_path='index.html', topic_slug=section_name)
        save_file(sub_index_path, sub_index_html)


def split_articles_to_categories(config):
    sections = OrderedDict()
    for topic in config['topics']:
        sections[topic['slug']] = []
    for article in config['articles']:
        article_data = {
            'title': article['title'],
            'href': get_page_href(page_source_path=article['source'], page_topic_slug=article['topic'])
        }
        sections[article['topic']].append(article_data)
    return sections


def markdown2html(markdown_text):
    return markdown.markdown(markdown_text,
                             extensions=[CodeHiliteExtension(),
                                         SmartyExtension()],
                             output_format='html5')


def make_article(source, title, topic_slug, topic_name):
    article_md = load_file(os.path.join(ARTICLES_PATH, source))
    if article_md is None:
        logging.error('Can\'t load file {}'.format(source))
        return
    article_html = markdown2html(article_md)
    data_to_template = {
        'page_topic_title': topic_name,
        'page_title': title,
        'text': article_html
    }
    resulting_html = render('article.html', context=data_to_template)
    article_path = get_saving_file_path(source, topic_slug)
    save_file(filepath=article_path, data_to_write=resulting_html)


def make_articles(config):
    topics = {e['slug']: e['title'] for e in config['topics']}
    for a_info in config['articles']:
        make_article(source=a_info['source'],
                     title=a_info['title'],
                     topic_slug=a_info['topic'],
                     topic_name=topics[a_info['topic']])


def check_config(config):
    unique_topics = set(elem['slug'] for elem in config['topics'])
    if len(unique_topics) != len(config['topics']):
        logging.error('Matching topic\'s slug! Topic slugs must be unique!')
        return False
    for article in config['articles']:
        if article['topic'] not in unique_topics:
            logging.error('Article {} has an unknown topic.'.format(article['source']))
            return False
    return True


def check_website(config):
    for article in config['articles']:
        article_path = get_saving_file_path(article['source'], article['topic'])
        if not os.path.exists(article_path):
            print('Error')


def copy_css():
    try:
        shutil.rmtree(HTML_PATH + '/css')
    except FileNotFoundError:
        pass
    shutil.copytree('templates/css', HTML_PATH + '/css')


def make_site():
    config = json.loads(load_file('config.json'))
    if check_config(config):
        make_indexes(config)
        make_articles(config)
        copy_css()
    else:
        print('Errors with config.json.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Static website generator')
    parser.add_argument('mode', nargs='?', help='Use `watch` to watch the changes and re-generate website', type=str)
    parameters = parser.parse_args()
    if parameters.mode is None:
        make_site()
    elif parameters.mode.lower() == 'watch':
        server = Server()
        server.watch('templates/*.html', make_site)
        server.watch('templates/css/*.css', copy_css)
        server.serve(root=HTML_PATH)
