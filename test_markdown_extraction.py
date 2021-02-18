import unittest
import extract_entries_from_markdown

class TestMarkdownExtraction(unittest.TestCase):
    
    def test_get_table_text_returns_empty_string_if_markdown_empty(self):
        md = '''
        '''

        expected = ''

        actual = extract_entries_from_markdown.get_table_text(md)
        self.assertEqual(actual, expected)

    def test_get_table_text_extracts_table_only(self):
        md = '''
        This is my markdown
        | Column | Headers | Are | Cool |
        ---------------------------------
        | Yep    | They    | Are | Yes  |
        
        # Heading
        '''

        expected = ''' 
        | Column | Headers | Are | Cool |
        ---------------------------------
        | Yep    | They    | Are | Yes  |'''.strip()
        expected = '\n'.join([line.strip() for line in expected.splitlines()])

        actual = extract_entries_from_markdown.get_table_text(md)
        self.assertEqual(actual, expected)

    def test_get_table_text_extracts_first_table_if_label_not_specified(self):
        md = '''
        This is my markdown
        | Column | Headers | Are | Cool |
        ---------------------------------
        | No | They    | Are | Not |
        
        # Heading
        | Another | Table |
        -----
        | Yep     | Another |
        '''

        expected = ''' 
        | Column | Headers | Are | Cool |
        ---------------------------------
        | No | They    | Are | Not |'''.strip()
        expected = '\n'.join([line.strip() for line in expected.splitlines()])

        actual = extract_entries_from_markdown.get_table_text(md)
        self.assertEqual(actual, expected)

    def test_get_table_text_extracts_labeled_table_if_specified(self):
        md = '''
        This is my markdown
        | Column | Headers | Are | Cool |
        ---------------------------------
        | No | They    | Are | Not |
        
        # My Target Table
        | Another | Table   |
        -----
        | Yep     | Another |

        Here is some other text
        | And | Another | Table |
        ---------------------------------
        | It  | Is      | Not   |
        | A   | Dining  | Table |
        '''

        expected = ''' 
        | Another | Table   |
        -----
        | Yep     | Another |'''.strip()
        expected = '\n'.join([line.strip() for line in expected.splitlines()])

        actual = extract_entries_from_markdown.get_table_text(md, target_heading_text="My Target Table")
        self.assertEqual(actual, expected)

    def test_table_to_rows_returns_empty_for_no_text(self):
        no_text_items = [None, '', ' ']
        expected = [] 

        for no_text_item in no_text_items:
            actual = extract_entries_from_markdown.table_to_rows(no_text_item)
            self.assertEqual(actual, expected)

    def test_table_to_dictionary_returns_entries_for_table(self):
        table_md = '''
        | First | Second | Third |
        -----
        | A | B | C |
        |   1  |  2   | 3   |
        | uno |   dos |    tres    |'''.strip()
        table_text = '\n'.join([line.strip() for line in table_md.splitlines()])

        expected = [
            {'First': 'A', 'Second': 'B', 'Third': 'C'},
            {'First': '1', 'Second': '2', 'Third': '3'},
            {'First': 'uno', 'Second': 'dos', 'Third': 'tres'}
        ]

        actual = extract_entries_from_markdown.table_to_rows(table_text)
        self.assertEqual(actual, expected)