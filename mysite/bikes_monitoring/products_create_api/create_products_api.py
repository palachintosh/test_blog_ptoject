from bikes_monitoring.PrestaRequest.mainp.PrestaRequest import PrestaRequest
from bikes_monitoring.PrestaRequest.mainp.api_secret_key import api_secret_key
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import ElementTree
import requests
import json
import re
import os.path


class ProductCreate(PrestaRequest):
    base_schema_path = os.path.dirname(os.path.abspath(__file__)) + '/schema'
    create_product_url = 'https://3gravity.pl/api/products/'
    create_combinations_url = 'https://3gravity.pl/api/combinations/'
    send_imgs_url = 'https://3gravity.pl/api/images/products/'
    tags_create_url = 'https://3gravity.pl/api/tags/'
    product_options_create_url = 'https://3gravity.pl/api/product_option_values/'
    product_xml = None
    current_product_id = None
    blank_xml = None
    errors_dict = {}
    dict_product_data = None
    same_product_information = None


    def _extract_tag(self, content, tag):
        # Function returns full tag content startin with given "tag" or None
        main_tag = ET.fromstring(content)

        xml_content = main_tag[0]
        final_tag = xml_content.find(tag)
        
        return final_tag if final_tag is not None else None


    def _return_tag_value(self, xml_content, tag):
        tag_value = ET.fromstring(xml_content)[0].find('id').text

        return tag_value


    def send_new_product_data(self, data=None):
        if data is None:
            with open(self.base_schema_path +'/new_xml_schema.xml','r') as f:
                data = f.read()

        if not data or data is None:
            self.errors_dict['data_error'] = 'Nie udało się sformować kartkę produktu.'
            return self.errors_dict
        
        send_create = requests.post(self.create_product_url, auth=(self.api_secret_key, ''), data=data.encode('utf-8'))

        if send_create.status_code >= 200 and send_create.status_code < 300:
            self.product_xml = send_create.text
            self.current_product_id = self._return_tag_value(self.product_xml, 'id')

            return {'success': 'Product ID: ' + self.current_product_id}
        
        else:
            self.errors_dict['product_add_error'] = 'Nie udało się dodać produktu. Serwer zwrócił kod: {}'.format(send_create.status_code)
            self.errors_dict['error_text'] = send_create.text
            
            return self.errors_dict


    def _add_new_attribute(self, url, data):
        if data is None or not data:
            return None
        
        add_new = requests.post(url, auth=(self.api_secret_key, ''), data=data.encode('utf-8'))

        if add_new.status_code >= 200 and add_new.status_code < 300:
            return add_new
            
        else:
            return None


    def edit_blank_xml(self, json_data):
        if not json_data:
            return {'error': 'Blank product data!'}

        self.dict_product_data = json_data

        with open(self.base_schema_path +'/blank_product_schema.xml') as f:
            xml_blank_data = f.read()


        # This dict helps to define fields in blank_product_schema.xml and change their text
        # to text from data.json without ifs
        assotiations_dict = {
            'meta_title': 'product_meta_title',
            'link_rewrite': 'product_meta_url',
            'meta_description': 'product_meta_description',
            'name': 'product_name',
            'description': 'product_long_description',
            'description_short': 'product_short_description',
            'combinations': 'product_combinations',
            'price': 'product_price',
        }

        # Parsing blank_product_schema.xml and define main tag - prestashop
        # xml_content =  ET.parse('blank_product_schema.xml')
        main_tag = ET.fromstring(xml_blank_data)
        xml_content = main_tag[0]


        # Find and all fields defines in the association dict (key) with data from data.json
        # Find data be (value)
        for key, value in assotiations_dict.items():
            parent_xml_tag = xml_content.find(key)
            if parent_xml_tag is None:
                continue
            
            if not list(parent_xml_tag):
                if key == 'price':
                    float_price = float(json_data[value]) / 1.23
                    final_price = "{0:.6f}".format(float_price)
                    parent_xml_tag.text = final_price
                else:
                    parent_xml_tag.text = json_data[value]
            
            else:
                get_first_language = parent_xml_tag.find('language')

                if get_first_language is not None:
                    get_first_language.text = json_data[value]
                    
        # xml_data = self.set_categories(xml_content)

        with open(self.base_schema_path + '/error_log.txt', 'a') as f:
            print("AFTER MAIN DATA ADDED", file=f)

        with_categories_data = self.set_categories(xml_content)


        with open(self.base_schema_path + '/error_log.txt', 'a') as f:
            print("AFTER CATEGORIES", file=f)


        if with_categories_data is not None:
            xml_data = with_categories_data

        write_xml = ElementTree(main_tag)
        write_xml.write(self.base_schema_path +'/new_xml_schema.xml')
        

        new_tags_array = [] # ElementTree objects

        if self.dict_product_data['product_meta_tags']:
            client_tags = self.dict_product_data['product_meta_tags'].split(',')
            if len(client_tags) > 0:
                for tag in client_tags:
                    if tag:
                        new_tag = self.add_new_tags(tag)

                        if new_tag is not None:
                            new_tags_array.append(new_tag)

                # And add tags to list with tags or just their
            
        with_tags_data = self.set_tags(xml_content, client_tags=new_tags_array)

        if with_tags_data is not None:
            xml_data = with_tags_data

        
        write_xml = ElementTree(main_tag)
        write_xml.write(self.base_schema_path +'/new_xml_schema.xml')
        
        # Send this data to prestashop
        xml_data = ET.tostring(main_tag, encoding='unicode')
        
        # create product
        add_product = self.send_new_product_data(data=xml_data)

        if isinstance(add_product, dict):
            if add_product.get('success') is not None:
                ############### After creating product ###############
                # Add combinations to existing product
                cr_combs = self.create_combs(json_data['product_combinations'])
                
                if len(cr_combs) > 0:
                    unable_combs = ''

                    for i in cr_combs:
                        unable_combs = unable_combs + i + ' '
                    
                    self.errors_dict['combinations_add_error'] = 'Nie udało się dodać tych kombinacji: {}'.format(unable_combs)

                # Add imgs because they need ids of new product
                send_imgs = self.get_imgs()

                if len(send_imgs) > 0:
                    unable_imgs = ''

                    for i in send_imgs:
                        unable_imgs = unable_imgs + i + ' '
                    
                    self.errors_dict['img_add_error'] = 'Nie udało się dodać niektórych zdjęć: {}'.format(unable_imgs)

                if self.errors_dict:
                    add_product['new_product_id'] = self.current_product_id
                    add_product['warnings'] = self.errors_dict

                    return add_product
                    
                else:
                    add_product['new_product_id'] = self.current_product_id
                    return add_product

        self.errors_dict['unexpected_error'] = 'Niespodziewany błąd podczas wysyłania informacji na 3gravity.pl'
        return self.errors_dict


    def define_product_options(self, comb_name):
        # Try to define valid option
        req_url = 'https://3gravity.pl/api/product_option_values?filter[name]={}'.format(comb_name)
        get_options = requests.get(req_url, auth=(self.api_secret_key, ''))

        if get_options.status_code != 200: return None
        get_options_url = self._extract_tag(get_options.content, 'product_option_value')
        
        if get_options_url is None:
            return self.add_new_options_value(comb_name)

        return get_options_url.attrib['id']

    
    def send_create_request(self, data):
        send_create = requests.post(self.create_combinations_url, auth=(self.api_secret_key, ''), data=data.encode('utf-8'))

        if send_create.status_code >= 200 and send_create.status_code < 300:
            return 'OK'
        
        return None


    def create_combs(self, comb_dict):
        # Opening blank scema
        combs_errors = []
        with open(self.base_schema_path +'/combinations.xml') as f:
            blank_data = f.read()

        xml_content = ET.fromstring(blank_data)
        main_tag = xml_content[0]

        for sku, comb_name in comb_dict.items():
            # Returns id
            get_product_options_id = self.define_product_options(comb_name)

            if get_product_options_id is None:
                self.errors_dict['comb_not_added'] = comb_name
                continue
            
            main_tag.find('id_product').text = self.current_product_id
            main_tag.find('reference').text = sku
            main_tag.find('associations').find('product_option_values')[0][0].text = get_product_options_id
            final_data = ET.tostring(xml_content, encoding='unicode')

            add_combination = self.send_create_request(final_data)

            if add_combination is None:
                combs_errors.append('Nie udało się dodać kimbinacji: {}'.format(comb_name))
        
        return combs_errors

    def get_imgs(self):
        img_errors = []
        send_img_url = self.send_imgs_url + self.current_product_id + '/'
        img_set = self.dict_product_data['product_img_urls_set']
        if not img_set:
            self.errors_dict['product_imgs_not_defined'] = 'Nie wybrano żadnego zdjęcia!'
            return []

        for img_url in img_set:
            get_img = requests.get(img_url)
            name = img_url.split('/')[-1]

            # img typ must be define in cortage
            files = {'image': (name, get_img.content, 'image/jpg')}

            send_img = requests.post(
                send_img_url,
                auth=(self.api_secret_key, ''),
                files=files)
            
            if send_img.status_code < 200 or send_img.status_code > 299:
                img_errors.append('Nie udało się dodać zdęcia: {}'.format(img_url))
        
        return img_errors
    

    def get_same_product(self):
        with open(self.base_schema_path + '/error_log.txt', 'a') as f:
            print("IN GET SAME PRODUCT", file=f)

        patt = re.compile('([A-Za-z ]+\d)')
        prod_model = patt.search(self.dict_product_data['product_name']).groups()

        with open(self.base_schema_path + '/error_log.txt', 'a') as f:
            print("PRODUCT_MODEL: " + str(prod_model), file=f)

        if prod_model is None:
            prod_model = self.dict_product_data['product_name'].split(' ')
            if len(prod_model) > 3:
                prod_model = ' '.join(prod_model[:3])
            
            else:
                prod_model = self.dict_product_data['product_name']
        
        else:
            prod_model = prod_model[0]
        

        with open(self.base_schema_path + '/error_log.txt', 'a') as f:
            print("PRODUCT_MODEL AFTER: " + str(prod_model), file=f)


        if prod_model is None:
            prod_model = self.dict_product_data['product_name']

        same_product_url = "https://3gravity.pl/api/products?filter[name]=%[{}]%".format(prod_model)
        same_product = requests.get(same_product_url, auth=(self.api_secret_key, ''))

        if same_product.status_code >= 200 and same_product.status_code < 300:
            xml_content = ET.fromstring(same_product.content) # [0]


            with open(self.base_schema_path + '/error_log.txt', 'a') as f:
                print("IN SAME PRODUCT CONTENT: " + str(xml_content), file=f)

            if xml_content is not None:
                xml_content = xml_content.find('products')
                if xml_content is None:
                    return None

            products_list = xml_content.findall('product')

            with open(self.base_schema_path + '/error_log.txt', 'a') as f:
                print("IN PRODUCTS LIST: " + str(len(products_list)), file=f)


            if products_list is not None:
                if len(list(products_list)) > 0:
                    get_first_product_id = list(products_list)[0].attrib['id']
                elif len(list(products_list)) > 1:
                    get_first_product_id = list(products_list)[1].attrib['id']

                with open(self.base_schema_path + '/error_log.txt', 'a') as f:
                    print("GET FIRST PRODUCT: " + str(get_first_product_id), file=f)

                # Save to class vars
                prod_info = requests.get(self.create_product_url + '/' + get_first_product_id, auth=(self.api_secret_key, ''))

                if prod_info.status_code >= 200 and prod_info.status_code < 300:
                    self.same_product_information = prod_info.content
                    with open(self.base_schema_path + '/error_log.txt', 'a') as f:
                        print("IN SAME PRODCUT INFO: " + str(prod_info.content), file=f)

                    return self.same_product_information
            
        return None


    def get_same_categories(self):
        with open(self.base_schema_path + '/error_log.txt', 'a') as f:
            print("IN GET SAME CATEGORIES", file=f)

        self.get_same_product()

        if self.same_product_information is not None:
            xml_content = ET.fromstring(self.same_product_information).find('product')
            if xml_content is None:
                self.errors_dict['same_product_not_found_warning'] = 'Nie udało się pobrać kategorii produktu.'
                return None

            cats = xml_content.find('associations').find('categories').findall('category')

            if cats:
                return cats
        
        self.errors_dict['same_product_not_found_warning'] = 'Nie udało się pobrać kategorii produktu.'
        return None


    def add_new_tags(self, tag_name):
        # client_tags_array = self.dict_product_data['product_meta_tags'].split(',')
        id_lang = '1' #because 3gravity has one (pl) language version with id=1

        with open(self.base_schema_path +'/tags_blank.xml') as f:
            blank_tags = f.read()

        main_tag = ET.fromstring(blank_tags)
        main_tag[0].find('id_lang').text = id_lang
        main_tag[0].find('name').text = tag_name
        xml_data = ET.tostring(main_tag, encoding='unicode')

        send_tag = self._add_new_attribute(self.tags_create_url, xml_data)

        if send_tag is not None:
            new_href_attrib = 'https://3gravity.pl/api/tags/'
            new_id = self._return_tag_value(send_tag.content, 'id')

            # Create new tag
            resp = ET.Element('tag', attrib={'ns0:href': new_href_attrib + new_id})
            ET.SubElement(resp, 'id').text = new_id

            return resp
        
        return None


    def get_relevant_options_category(self):
        url = 'https://3gravity.pl/api/product_options?filter[name]=[{}]'.format(
                self.dict_product_data['product_combinations_type'])

        get_category = requests.get(url, auth=(self.api_secret_key, ''))

        if get_category.status_code >= 200 and get_category.status_code < 300:
            id = self._extract_tag(get_category.content, 'product_options')

            if id is not None:
                return id.attrib['id']

            else: return '1'


    def add_new_options_value(self, comb_name):
        with open(self.base_schema_path +'/product_options_blank.xml') as f:
            blank_options = f.read()
        
        rel_category_id = self.get_relevant_options_category()
        
        main_tag = ET.fromstring(blank_options)
        main_tag[0].find('id_attribute_group').text = rel_category_id
        main_tag[0].find('name')[0].text = comb_name
        xml_data = ET.tostring(main_tag, encoding='unicode')

        send_option_value = self._add_new_attribute(self.product_options_create_url, xml_data)

        if send_option_value is not None:
            return self._return_tag_value(send_option_value.content, 'id')
            
        return None


    def get_same_tags(self):
        if self.same_product_information is not None:
            xml_content = ET.fromstring(self.same_product_information).find('product')
            if xml_content is None:
                self.errors_dict['same_product_no_tags_warning'] = 'Nie udało się pobrać tagów produktu.'
                return None

            tags = xml_content.find('associations').find('tags').findall('tag')

            if tags:
                return tags
        
        self.errors_dict['same_product_no_tags_warning'] = 'Nie udało się pobrać tagów produktu.'
        return None


    def set_tags(self, xml_content, client_tags=[]):
        new_tags = self.get_same_tags()

        if new_tags is None:
            return None

        if isinstance(client_tags, list):
            new_tags = new_tags + client_tags

        np = xml_content.find('associations').find('tags')
        
        for tag in new_tags:
            np.insert(0, tag)

        return np


    def set_categories(self, xml_content):
        with open(self.base_schema_path + '/error_log.txt', 'a') as f:
            print("IN SET CATEGORIES", file=f)

        new_categories = self.get_same_categories()
        np = xml_content.find('associations').find('categories')
        
        if new_categories is None:
            return None

        for cat in new_categories:
            np.insert(0, cat)

        return np
