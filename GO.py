#!/usr/bin/env python3
        
class GO:
    ''' A class to represent GO ojects.

        Attributes
        ----------
        categories: dictionary with GO id as key and GO_category objects 
                    as values
        relations:  dictionary with 'typedef' (e.g., is_a) as key 
                    and GO_relation objects as values

        Methods
        -------
        _read(self, filename):
            reads the Gene Ontology database file
        
        _init_relations(self):
            initializes the relations
        
        invert(self, category1, category2, relation='part_of'):
            Simple function to revert relationship
            (Solution 1 for task 4)
        
        combine_two_relations(self, category, rel1, rel2, new_relation='myrel'):
            Combines two relations into new relation
            (Solution 1 for task 5)
        
        combine_specific_relations(self, category, to_combine, new_relation='myrel'):
            Combines specific relations instances
            (Solution 2 for task 5)
    '''

    def __init__(self, filename):
        ''' Initiate the Go object
        
            Constructs all the necessary instance attributes for the GO object
            and runs '_read' and '_init_relations' methods.

            Parameters
            ----------
            filename: name of the Gene Ontology database file
        '''

        self.categories = {}
        # adds the is_a relation to the object cause it is not
        # as a '[Typedef]' in the go.obo file
        self.relations = {
            'is_a': GO_relation({'id': ['is_a'],
                                 'name': ['is_a'],
                                 'is_transitive': [True]})
        }
        self._read(filename)
        self._init_relations()
    

    def _read(self, filename):
        ''' Reads the Gene Ontology database file.
            
            Creating key (category id), value (Go_category objects) pairs for the categories dictionary.
            Creating key (relationship id), value (Go_relation objects) pairs for the relations dictionary.
        
            Parameters
            ----------
            filename: name of the Gene Ontology database file
        '''

        with open(filename, 'r') as f:
            section = ''
            attributes = {}
            for line in f:
                line = line.strip()
                if line == '':
                    if section == 'Term':
                        category = GO_category(attributes)
                        self.categories[category.id] = category
                    elif section == 'Typedef':
                        relation = GO_relation(attributes)
                        self.relations[relation.id] = relation
                    attributes.clear()
                    section = ''
                elif line.startswith('[') and line.endswith(']'):
                    # sets section to either 'Term' or 'Typedef'
                    section = line[1:-1]
                else:
                    k, v = line.split(': ', 1)
                    try:
                        attributes[k].append(v)
                    except KeyError:
                        attributes[k] = [ v ]

    def _init_relations(self):
        ''' Initiate the relations of the GO_relation 'pairs' attribute

            We have already read the file and filled the categories and relations 
            dictionaries. Now we need to add the relations that are in the GO_categories
            'others' attribute to the 'pairs' attribute of the GO_relation object.
            This can be a 'is_a' relation but also other relationship types (e.g., part of)

            Pairs is a dictionary with GO_category id as key and 
            another GO_category id as value. 
        '''
       
        # get the GO_relation object for 'is_a'           
        is_a = self.relations['is_a']
        # category is a Go_category object
        for go, category in self.categories.items():
            if 'is_a' in category.others:
                for value in category.others['is_a']:
                    other_go, _ = value.split(' ! ', 1)
                    other_category = self.categories[other_go]
                    is_a.add_pair(category, other_category)
                del category.others['is_a']
            # adds pairs of other relationship types to relations attribute
            if 'relationship' in category.others:
                for value in category.others['relationship']:
                    rel, other_go, _ = value.split(' ', 2)
                    # get the GO_category oject for other category
                    other_category = self.categories[other_go]
                    self.relations[rel].add_pair(category, other_category)
                del category.others['relationship']

    # Task 4 Implement inverting relations
    # potential solution1
    # Placing the function here makes calling it more straight forward
    # e.g., go.invert(category1, category2, relation)
    def invert(self, category1, category2, relation='part_of'):
        ''' Simple function to revert relationship

            Parameters
            ----------
            category1:  GO_category object of Go term to check relation for
            category2:  GO_category object of GO term to check if it is in
                        relation to category 1
            relation:   which type of relation to check

            Returns
            -------
            list
                list of two G0_category objects that indicates switched relation.
                e.g., [category2, category1] 
        '''

        if not isinstance(category1, GO_category):
            raise TypeError('category1 must be a GO_category.')
        if not isinstance(category2, GO_category):
            raise TypeError('category2 must be a GO_category.')
        
        if category2 in self.relations[relation][category1]:
            return [category2, category1]
        else:
            print("{} and {} are not related through '{}'".format(category2, category1, relation))


    # Task 5 Implement combining relations (solution 1)
    # Combines two relationship classes into a new one
    def combine_two_relations(self, category, rel1, rel2, new_relation='myrel'):
        ''' Combines two relations into new relation

            Combines all the GO_category entries of the passed relations and 
            saves it as new realtion.

            Parameters
            ----------
            category:       GO_category object of category to combine relation for
            rel1:           name of relation that should be combined
            rel2:           name of other relation that should be combined
            new_relation:   name of new realation
        '''
        # check if category is a GO_category object
        if not isinstance(category, GO_category):
            raise TypeError('category must be a GO_category.')

        # create new relation type in relations attribute
        self.relations.update({new_relation: GO_relation({'id': [new_relation],
                                                    'name': [new_relation],
                                                    'is_transitive': [False]})
        })

        relation1_rels=self.relations[rel1][category]
        relation2_rels=self.relations[rel2][category]
        combined_rels=relation1_rels.union(relation2_rels)

        self.relations[new_relation].pairs[category] = combined_rels
    
        

    # Task 5 Implement combining specific relations (solution 2)
    # similar to the combine_two_relations function
    # but handles specific G0 categories and their relation as input
    # TODO currently not working when there is two relations with the same 
    # relation type (e.g., 'is_a') in the input dictionary
    def combine_specific_relations(self, category, to_combine, new_relation='myrel'):
        ''' Combines specific relations instances

            Combines specific GO_categories of relations and 
            saves it as new realtion.

            Parameters
            ----------
            category:       GO_category object of category to combine relations for
            to_combine:     dictionary with Typedef id (e.g., 'is_a') as keys and 
                            GO id (e.g., "GO:0000022") as values
            new_relation:   name of new realation

        '''

        # TODO check if to_combine has the right input format
 
        # create new relation type in relations attribute
        self.relations.update({new_relation: GO_relation({'id': [new_relation],
                                                    'name': [new_relation],
                                                    'is_transitive': [False]})
        })

        combined_rels= set()

        # loop over input dictionary
        for r, c in to_combine.items():
            tmp_category=self.categories[c]
            if tmp_category in self.relations[r][category]:
                combined_rels.add(tmp_category)

        self.relations[new_relation].pairs[category] = combined_rels


def _pop_single_value(k, values):
    ''' Pops a single entry from the dict accoring to key.

        parses through dict that is passed to the function and returns
        the value for the key (k) and then deletes the entry from the dict.
        Similar to the pop() method. 
    '''

    if len(values[k]) != 1:
        raise ValueError('There must be exactly one element in values.')
    value = values[k][0]
    del values[k]
    return value


class GO_category:
    ''' A class to represent GO category objects

        Attributes
        ----------
            id:         id of the GO category
            name:       name of the GO category
            definition: description of the GO category function
            others:     further attributes of the GO category

        Methods
        -------
        __repr__(self):
            returning a representation of the class.
        
        __lt__(self, other):
            Compares the id attributes of two ojects and
            defines the behavior of the < operator for objects
    '''

    def __init__(self, attributes):
        '''Initiate the Go_category object

            Parameters
            ----------
            attributes: dictionary of attributes
        '''

        # found the bug. We needed to copy the attributes.
        # this ensures that the GO_category has it's own set of
        # attributes. It also prevents the attributes to be manipulated
        # later in the code. 
        attributes = attributes.copy()
        self.id = _pop_single_value('id', attributes)
        self.name = _pop_single_value('name', attributes)
        self.definition = _pop_single_value('def', attributes)
        self.others = attributes

    def __repr__(self):
        return '{} ({})'.format(self.id, self.name)

    def __lt__(self, other):
        return self.id < other.id

    
class GO_relation:
    ''' A class to represent GO relation objects

        Attributes
        ----------
            id:             id of the GO relation
            name:           name of the GO relation
            is_transitive:  boolean value if relation is transitive
            others:         further attributes of the GO relation
            pairs:          dictionary of relationship pairs with 
                            'typedef' (e.g., is_a) as key

        Methods
        -------
        __repr__(self):
            returning a representation of the class in form of the
            Go relation id. 

        add_pair(self, category1, category2):
            adds a relationship pair (i.e. pair of categories) to the
            pairs attribute (dictionary)

        __contains__(self, pair):
            defines the behavior for the in operator.
            Working on the pairs attribute

        __getitem__(self, category):
            defines how an object retrieves an item using the square bracket notation ([])
            Working on the pairs attribute

        __iter__(self):
            function returns an iterator for the pairs attribute

        copy(self):
            creates a new instance of the class and copies the attributes 
            and relationships from the current instance to the new one
        
        __eq__(self, other):
            Takes two relation ojects and compares if their attributes 
            are the same. Returns tuple of boolean values.
        
        invert_rel(self, category1, category2, relation='part_of'):
             Simple function to revert relationship
             (Solution 2 for task 4)
    '''

    def __init__(self, attributes):
        ''' Initiate the Go_relation object

            Parameters
            ----------
            attributes: dictionary of attributes
        '''

        attributes = attributes.copy()
        self.id = _pop_single_value('id', attributes)
        self.name = _pop_single_value('name', attributes)
        self.is_transitive = ('is_transitive' in attributes and
                              str(_pop_single_value('is_transitive', attributes)).lower() != 'false')
        self.others = attributes
        self.pairs = {}
        
    def __repr__(self):
        return '<{}>'.format(self.id)
    
    def add_pair(self, category1, category2):
        if not isinstance(category1, GO_category):
            raise TypeError('category1 must be a GO_category.')
        if not isinstance(category2, GO_category):
            raise TypeError('category2 must be a GO_category.')
        try:
            self.pairs[category1].add(category2)
        except KeyError:
            self.pairs[category1] = { category2 }

    def __contains__(self, pair):
        if (not isinstance(pair, tuple) or len(pair) != 2 or
            not isinstance(pair[0], GO_category) or not isinstance(pair[1], GO_category)):
            raise TypeError('pair must be a tuple of two GO_category objects.')
        try:
            return pair[1] in self.pairs[pair[0]]
        except KeyError:
            return False

    def __getitem__(self, category):
        if not isinstance(category, GO_category):
            raise TypeError('category must be a GO_category.')
        try:
            return self.pairs[category]
        except KeyError:
            return set()
        
    def __iter__(self):
        for category1 in self.pairs:
            for category2 in self.pairs[category1]:
                yield category1, category2

    def copy(self):
        cls = self.__class__
        result = cls.__new__(cls)
        attributes = {'id': [self.id], 'name': [self.name], 'is_transitive': [self.is_transitive]}
        attributes.update(self.others)
        result.__init__(attributes)
        for category1, category2 in self:
            result.add_pair(category1, category2)
        return result

    def __eq__(self, other):
        return (self.id == other.id and
                self.name == other.name and
                self.is_transitive == other.is_transitive and
                self.others == other.others and
                self.pairs == other.pairs)
    
    # Task 4 Implement inverting relations
    # potential solution2
    # Placing the function here makes calling it more layered
    # e.g., go.relations[rel].invert_rel(category1, category2)
    # TODO I don't think we need to pass a relation with this fuction
    # as we can just refer to the instance relation as self.id (change function)
    def invert_rel(self, category1, category2, relation='part_of'):
        ''' Simple function to revert relationship

            Parameters
            ----------
            category1:  GO_category object of Go term to check relation for
            category2:  GO_category object of GO term to check if it is in
                        relation to category 1
            relation:   which type of relation to check

            Returns
            -------
            list
                list of two G0_category objects that indicates switched relation.
                e.g., [category2, category1] 
        '''

        if not isinstance(category1, GO_category):
            raise TypeError('category1 must be a GO_category.')
        if not isinstance(category2, GO_category):
            raise TypeError('category2 must be a GO_category.')
        
        # need to use __contains__ as we are manipulating the 'in'
        # operators behaviour beforehand
        if self.pairs[category1].__contains__(category2):
            return [category2, category1]
        else:
            print("{} and {} are not related through '{}'".format(category2, category1, relation))


### TASK 6 ###
# Unfortunatley I didn't get far with Task 6 in the time I had
# but I will be working on this task until Friday so we can 
# discuss it more. 

