import unittest

import utilities.fileutils as fu
import pandas as pd

from unittest.mock import patch, Mock

class TestFileFunctions(unittest.TestCase):




    def setUp(self):
        self.CSV_ONE = '~/smith/cats.csv'
        self.CSV_TWO = '~/smith/dogs.csv'
        self.XLS_ONE = '~/smith/fish.xls'

        frame1 = {'sequence': [3, 2, 1],
                  'agg': [ 3, 20, 10]
                  }
        frame2 = {'sequence': [3, 2, 2, 1],
                  'agg': [10, 20, 20, 30]
                  }
        referenced_frame1 = {
                  'sequence': ['foo', 'bar', '13@z'],
                  'File Name 1': ['cats.csv', 'cats.csv', 'cats.csv'],
                  'agg': [3, 20, 10]
                  }
        referenced_frame2 = {
            'sequence': ['foo', 'fizz', 'rot13'],
            'File Name 1': ['dogs.csv', 'dogs.csv', 'dogs.csv'],
            'agg': [3, 20, 10]
        }

        expected_agg_frame = {
            'sequence': [2, 3, 1, 3, 1],
            'agg': [20, 3, 10, 10, 30],
            'Occurence': [3, 1, 1, 1, 1]
        }

        self.PD_DF1 = pd.DataFrame(frame1)
        self.PD_DF2 = pd.DataFrame(frame2)
        self.PD_RDF1 = pd.DataFrame(referenced_frame1)
        self.PD_RDF2 = pd.DataFrame(referenced_frame2)
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

    @patch('utilities.fileutils.os')
    def test_return_filetype_list_happy_case(self, mock_os):
        mock_os.fsencode.return_value = self.FILEPATH
        mock_os.listdir.return_value = self.RETURNED_FILELIST

        expected_value = [self.CSV_ONE, self.CSV_TWO]
        actual_value = fu.return_filetype_list(self.FILEPATH, filetype=".csv")

        mock_os.listdir.assert_called_with(self.FILEPATH)

        self.assertEquals(actual_value, expected_value, "return file type returns only files with specified type" )


    @patch('utilities.fileutils.pd.read_csv')
    @patch('utilities.fileutils.create_aggregate_dataframe')
    @patch('utilities.fileutils.return_filetype_list')
    def test_matchlist(self, mock_get_files, mock_agg_frame, mocked_reader):
        mock_get_files.return_value = [self.CSV_ONE, self.CSV_TWO]
        mocked_reader.side_effect = lambda key: self.DF_NAME_TO_DATAFRAME[key]

        stump_df = Mock()
        mock_agg_frame.return_value = stump_df

        fu.matchlist('~/smith', '~smith/output', 'sequence', 'agg')

        assert mock_agg_frame.called

    def test_write_dataframe_to_csv(self):
        with patch.object(fu.pd.DataFrame, "to_csv") as mocked_writer:
            stump_df = Mock()
            stump_df.to_csv = mocked_writer
            fu.write_dataframe_to_csv(stump_df, "foo.csv")

            mocked_writer.assert_called_once()



    def test_aggregate_frame_happy_case(self):
        actual_result = fu.create_aggregate_dataframe([self.PD_DF1, self.PD_DF2], 'sequence', 'agg')
        expected_result = self.PD_AGG_DF1.sort_values(by=['Occurence', 'agg'], ascending=[False, True])
        expected_result = expected_result[['sequence', 'agg', 'Occurence']] #column order was affecting equality check; this will make fragile if more columns are added.

        self.assertEquals(expected_result.equals(actual_result), True)


    @patch('utilities.fileutils.make_file_referenced_df_from_csv')
    @patch('utilities.fileutils.openfiles')
    def test_combinedlist_happy_case(self, mock_get_files, mock_make_df):
        mock_get_files.return_value = [self.CSV_ONE, self.CSV_TWO]
        mock_make_df.side_effect = lambda key: self.DF_NAME_TO_DATAFRAME[key]




