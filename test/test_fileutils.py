import unittest
import os

import utilities.fileutils as fu
import pandas as pd

from unittest.mock import patch, Mock

class TestFileFunctions(unittest.TestCase):




    def setUp(self):
        self.CSV_ONE = 'cats.csv'
        self.CSV_TWO = 'dogs.csv'
        self.XLS_ONE = 'fish.xls'

        self.AGG_DICT = {
            'key1' : [1, 2, 3],
            'key2' : [4, 5, 6]
        }
        frame1 = {'sequence': ['c', 'b', 'a'],
                  'agg': [ 3, 20, 10],
                  'file': ['cats.csv', 'cats.csv', 'cats.csv']
                  }
        frame2 = {'sequence': ['b', 'b', 'a'],
                  'agg': [20, 20, 30],
                  'file': ['dogs.csv', 'dogs.csv', 'dogs.csv']
                  }
        referenced_frame1 = {
                  'sequence': ['foo', 'bar', '13@z'],
                  'file': ['cats.csv', 'cats.csv', 'cats.csv'],
                  'agg': [3, 20, 10]
                  }
        referenced_frame2 = {
            'sequence': ['foo', 'fizz', 'rot13'],
            'file': ['dogs.csv', 'dogs.csv', 'dogs.csv'],
            'agg': [3, 20, 10]
        }

        referenced_3_frame1 = {
            'sequence': ['foo', 'bar'],
            'file': ['cats.csv', 'cats.csv'],
            'agg': [3, 20]
        }

        referenced_4_frame1 = {
            'sequence': ['13@z'],
            'file': ['cats.csv'],
            'agg': [10]
        }

        expected_agg_frame = {
            'sequence': ['a', 'b', 'c'],
            'Occurrence': [2, 3, 1],
            'cats.csv': [1, 1, 1],
            'dogs.csv': [1, 2, 0]
        }

        self.PD_DF1 = pd.DataFrame(frame1)
        self.PD_DF2 = pd.DataFrame(frame2)
        self.PD_RDF1 = pd.DataFrame(referenced_frame1)
        self.PD_RDF2 = pd.DataFrame(referenced_frame2)
        self.PD_RD3DF1 = pd.DataFrame(referenced_3_frame1)
        self.PD_RD4DF1 = pd.DataFrame(referenced_4_frame1)
        self.PD_AGG_DF1 = pd.DataFrame(expected_agg_frame)

        self.DF_NAME_TO_DATAFRAME = {
            self.CSV_ONE: self.PD_DF1,
            self.CSV_TWO: self.PD_DF2,
        }

        self.DF_NAME_TO_REFERENCED_DATAFRAME = {
            self.CSV_ONE: self.PD_RDF1,
            self.CSV_TWO: self.PD_RDF2,
        }

        self.RETURNED_FILELIST = [self.CSV_ONE,
                                  self.XLS_ONE,
                                  self.CSV_TWO
                                  ]


        self.FILEPATH = '~/smith/'

    @patch('utilities.fileutils.os.listdir')
    @patch('utilities.fileutils.os.fsencode')
    def test_return_filetype_list_happy_case(self, mock_os_fsencode, mock_os_listdir):
        mock_os_fsencode.return_value = self.FILEPATH
        mock_os_listdir.return_value = self.RETURNED_FILELIST

        expected_value = [os.path.sep.join([self.FILEPATH, self.CSV_ONE]),
                          os.path.sep.join([self.FILEPATH, self.CSV_TWO])]
        actual_value = fu.return_filetype_list(self.FILEPATH, filetype=".csv")

        mock_os_listdir.assert_called_with(self.FILEPATH)

        self.assertEquals(actual_value, expected_value, "return file type returns only files with specified type" )


    @patch('utilities.fileutils.pd.read_csv')
    @patch('utilities.fileutils.create_aggregate_sequence_dataframe')
    @patch('utilities.fileutils.return_filetype_list')
    def test_aggregate_sequence_occurence_by_length_happy_case(self, mock_get_files, mock_agg_frame, mocked_reader):
        mock_get_files.return_value = [self.CSV_ONE, self.CSV_TWO]
        mocked_reader.side_effect = lambda key: self.DF_NAME_TO_DATAFRAME[key]

        stump_df = Mock()
        mock_agg_frame.return_value = stump_df

        fu.aggregate_sequence_occurence_by_length('~/smith', 'sequence', 'agg')

        assert mock_agg_frame.called

    def test_write_dataframe_to_csv(self):
        with patch.object(fu.pd.DataFrame, "to_csv") as mocked_writer:
            stump_df = Mock()
            stump_df.to_csv = mocked_writer
            fu.write_dataframe_to_csv(stump_df, "foo.csv")

            mocked_writer.assert_called_once()

    def test_create_match_dataframe_single_pattern(self):
        pattern_list = ["^f"]
        all, some, none_df = fu.create_match_dataframes(pattern_list, self.PD_RDF1, 'sequence')
        print("all was : {}".format(all))
        print("some was : {}".format(some))
        print("none_df was : {}".format(none_df))

    def test_create_match_dataframe_happy_case(self):
        pattern_list = ["^[a-z]", "^f"]
        all, some, none_df = fu.create_match_dataframes(pattern_list, self.PD_RDF1, 'sequence')
        print("all was : {}".format(all))
        print("some was : {}".format(some))
        print("none_df was : {}".format(none_df))

    def test_make_columns_from_dict(self):
        expected_result = pd.DataFrame({"keyz": ["key1", "key1", "key1", "key2", "key2", "key2"],
                                        "vals": [1, 2, 3, 4, 5, 6]})
        print(expected_result)
        actual_result = fu.make_columns_from_dict(self.AGG_DICT,
                                                  primary_col_name="keyz",
                                                  secondary_col_name="vals")

        print(expected_result.keys())
        print(actual_result.keys())

        self.assertEqual(list(expected_result.keys()), list(actual_result.keys()))

        for i in range(expected_result.shape[0]):
            self.assertEquals(expected_result.iloc[i]['keyz'], actual_result.iloc[i]['keyz'])
            self.assertEquals(expected_result.iloc[i]['vals'], actual_result.iloc[i]['vals'])


    def test_aggregate_frame_happy_case(self):
        test_input = pd.concat([self.PD_DF1, self.PD_DF2])
        actual_result = fu.create_aggregate_sequence_dataframe(test_input, 'sequence', 'file')
        expected_result = self.PD_AGG_DF1.sort_values(by=['sequence'], ascending=[True])
        expected_result = expected_result[['sequence', 'Occurrence',  'cats.csv',  'dogs.csv']] #column order was affecting equality check; this will make fragile if more columns are added.

        for i in range(expected_result.shape[0]):
            self.assertEquals(expected_result.iloc[i]['sequence'], actual_result.iloc[i]['sequence'])
            self.assertEquals(expected_result.iloc[i]['Occurrence'], actual_result.iloc[i]['Occurrence'])
            self.assertEquals(expected_result.iloc[i]['cats.csv'], actual_result.iloc[i]['cats.csv'])
            self.assertEquals(expected_result.iloc[i]['dogs.csv'], actual_result.iloc[i]['dogs.csv'])


    @patch('utilities.fileutils.make_file_referenced_df_from_csv')
    @patch('utilities.fileutils.openfiles')
    def test_combinedlist_happy_case(self, mock_get_files, mock_make_df):
        mock_get_files.return_value = [self.CSV_ONE, self.CSV_TWO]
        mock_make_df.side_effect = lambda key: self.DF_NAME_TO_DATAFRAME[key]

    def test_split_df_by_col_length_happy_case(self):
        expected_result = {3: self.PD_RD3DF1, 4: self.PD_RD4DF1}
        actual_result = fu.split_df_by_col_length(self.PD_RDF1, "sequence")

        self.assertEqual(expected_result.keys(), actual_result.keys())

        for key in expected_result.keys():
            for i in range(expected_result[key].shape[0]):
                self.assertEquals(expected_result[key].iloc[i]['sequence'], actual_result[key].iloc[i]['sequence'])
                self.assertEquals(expected_result[key].iloc[i]['file'], actual_result[key].iloc[i]['file'])
                self.assertEquals(expected_result[key].iloc[i]['agg'], actual_result[key].iloc[i]['agg'])

