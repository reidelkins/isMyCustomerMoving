import React, { useEffect, useState, useMemo } from 'react';
import {
  Card,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow,
  Typography,
  Stack,
  IconButton,
} from '@mui/material';
import PropTypes from 'prop-types';

import Scrollbar from './Scrollbar';
import Iconify from './Iconify';
import { ReferralListHead } from '../sections/@dashboard/referral';

const ReferralsData = ({ refs, company, incoming }) => {
  const emptyRows = 0;
  const [referrals, setReferrals] = useState([]);
  const fakeData = useMemo(
    () => [
      {
        client: { name: 'Ethan Johnson', phoneNumber: '656-674-2287' },
        referredTo: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: { id: 'WUFH4VbW', name: 'AAA Water Systems' },
        contacted: false,
      },
      {
        client: { name: 'Olivia Smith', phoneNumber: '713-435-9560' },
        referredTo: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: { id: 'OIJBMu7k', name: 'AAA Water' },
        contacted: false,
      },
      {
        client: { name: 'Liam Martinez', phoneNumber: '336-440-8988' },
        referredTo: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: { id: 'MPUPthKq', name: 'KWater' },
        contacted: false,
      },
      {
        client: { name: 'Emma Thompson', phoneNumber: '259-527-2654' },
        referredTo: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: { id: 'OGok4U65', name: 'A Plus Water Solution' },
        contacted: false,
      },
      {
        client: { name: 'Noah Wilson', phoneNumber: '650-610-5081' },
        referredTo: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: { id: 's1TfSF6o', name: 'Specialty Water' },
        contacted: false,
      },
      {
        client: { name: 'Ava Davis', phoneNumber: '166-146-8554' },
        referredTo: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: {
          id: '3LqyyhHL',
          name: 'Superior Water Conditioning Inc.',
        },
        contacted: false,
      },
      {
        client: { name: 'Oliver Anderson', phoneNumber: '673-379-4677' },
        referredTo: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: { id: 'qBiB0Cd3', name: 'Advanced Water - VA' },
        contacted: false,
      },
      {
        client: {
          name: 'Isabella Rodriguez',
          phoneNumber: '427-746-6828',
        },
        referredTo: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: {
          id: 'HtsB7HW3',
          name: 'ABC Water Conditioning Service',
        },
        contacted: false,
      },
      {
        client: { name: 'Lucas Moore', phoneNumber: '800-812-3562' },
        referredTo: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: { id: 'POfSdmXp', name: 'Advantaged Water' },
        contacted: false,
      },
      {
        client: { name: 'Sophia Turner', phoneNumber: '796-854-1410' },
        referredTo: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: { id: 'MKqjfWio', name: 'Aon Water Technology' },
        contacted: false,
      },
      {
        client: { name: 'Mason Clark', phoneNumber: '279-318-9080' },
        referredTo: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: { id: 'bUehkpTl', name: 'Aqua Soft Water Systems' },
        contacted: false,
      },
      {
        client: { name: 'Mia Lewis', phoneNumber: '187-844-5794' },
        referredTo: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: { id: 'hDJZuM7X', name: 'Aqua Systems' },
        contacted: false,
      },
      {
        client: { name: 'Benjamin White', phoneNumber: '401-493-3330' },
        referredTo: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: {
          id: 'O7Fwl2gm',
          name: 'Aqua Clear Water Solutions',
        },
        contacted: false,
      },
      {
        client: { name: 'Charlotte Hill', phoneNumber: '133-340-9568' },
        referredTo: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: {
          id: 'qYTZu8rx',
          name: 'Aqua-Sure Water Conditioning',
        },
        contacted: false,
      },
      {
        client: { name: 'Henry Scott', phoneNumber: '202-932-4189' },
        referredTo: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: { id: 'vP1ECvK7', name: 'Aquarius Water' },
        contacted: false,
      },
      {
        client: { name: 'Amelia Walker', phoneNumber: '257-325-7982' },
        referredTo: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: { id: 'p1OyOZdv', name: 'Atlantis Water Systems' },
        contacted: false,
      },
      {
        client: { name: 'Alexander Young', phoneNumber: '671-511-5820' },
        referredTo: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: {
          id: 'Uy6Pol2q',
          name: 'B & J Water Conditioning',
        },
        contacted: false,
      },
      {
        client: { name: 'Harper Adams', phoneNumber: '739-287-7011' },
        referredTo: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: { id: 'ug83zt1n', name: 'Automatic Water Inc.' },
        contacted: false,
      },
      {
        client: { name: 'William Mitchell', phoneNumber: '664-472-8283' },
        referredTo: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: {
          id: '808SVkMG',
          name: 'Atlantic Coast Water Cond. Inc.',
        },
        contacted: false,
      },
      {
        client: { name: 'Evelyn Rivera', phoneNumber: '836-768-9401' },
        referredTo: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: { id: 'aBjDP8pn', name: 'Better Water, Inc.' },
        contacted: false,
      },
      {
        client: { name: 'James Carter', phoneNumber: '343-314-1630' },
        referredTo: { id: 'LgVL0bym', name: 'Best Water Systems Inc.' },
        referredFrom: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Abigail Reed', phoneNumber: '639-450-8523' },
        referredTo: { id: 'kFjrEvg6', name: 'Besco Water Treatment' },
        referredFrom: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Michael Wright', phoneNumber: '486-713-4202' },
        referredTo: { id: 'zUNNjOUI', name: 'CGC Water' },
        referredFrom: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Emily Coleman', phoneNumber: '416-985-3920' },
        referredTo: {
          id: 'WbLUpKaQ',
          name: 'Central Florida Water Systems Inc.',
        },
        referredFrom: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Daniel Bell', phoneNumber: '294-771-7700' },
        referredTo: { id: 'UA8kCxeF', name: 'Citrus Water Conditioning' },
        referredFrom: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Elizabeth Green', phoneNumber: '169-255-8947' },
        referredTo: { id: 'cWGa3TxB', name: 'Chatts Worth Water' },
        referredFrom: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Elijah Brooks', phoneNumber: '881-312-1583' },
        referredTo: { id: 's9uTQqZy', name: 'Clear Water Systems' },
        referredFrom: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Sofia Perry', phoneNumber: '758-101-6781' },
        referredTo: { id: 'a5P0QxPR', name: 'Clarksville Water' },
        referredFrom: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Matthew Cox', phoneNumber: '704-399-7997' },
        referredTo: {
          id: '2ljl1RVa',
          name: 'Custom Water Solutions, Inc.',
        },
        referredFrom: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Avery Bailey', phoneNumber: '707-751-6137' },
        referredTo: { id: 'KtTuXYzv', name: 'Clearwater Systems' },
        referredFrom: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'David Reed', phoneNumber: '866-121-4212' },
        referredTo: { id: 'L1csKyQI', name: 'Flag City Water Systems' },
        referredFrom: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Ella James', phoneNumber: '957-982-9077' },
        referredTo: { id: 'E5YVW9yk', name: 'Elite Water and Coffee' },
        referredFrom: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: {
          name: 'Jackson Richardson',
          phoneNumber: '427-286-5861',
        },
        referredTo: { id: 'qfBXQrrh', name: 'Flatwater Grill' },
        referredFrom: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Victoria Price', phoneNumber: '417-770-2979' },
        referredTo: { id: 'AZdiy9zN', name: 'Hague' },
        referredFrom: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Logan Murphy', phoneNumber: '848-782-6222' },
        referredTo: { id: '1qAnxZU5', name: 'Hart Water' },
        referredFrom: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Grace Nelson', phoneNumber: '125-350-6859' },
        referredTo: { id: 'CWwHmTS0', name: 'Hague Quality Water' },
        referredFrom: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Sebastian Foster', phoneNumber: '992-511-1026' },
        referredTo: { id: 'INRksjVZ', name: 'Hydrotech' },
        referredFrom: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Lily Henderson', phoneNumber: '847-286-9018' },
        referredTo: {
          id: 'yQK4kjfQ',
          name: 'Household Water Specialist',
        },
        referredFrom: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Joseph Ross', phoneNumber: '691-733-2331' },
        referredTo: { id: 'MkEWVDgh', name: 'Kinetico - American Water' },
        referredFrom: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Scarlett Ramirez', phoneNumber: '638-318-5213' },
        referredTo: {
          id: 'InJc8vdH',
          name: 'K & J of South Florida, Inc.',
        },
        referredFrom: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Samuel Roberts', phoneNumber: '344-477-5091' },
        referredTo: {
          id: 'jQaxZvLl',
          name: 'Kinetico - Martin Water Conditioning',
        },
        referredFrom: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Chloe Ward', phoneNumber: '134-678-5774' },
        referredTo: {
          id: 'aPW03VYf',
          name: 'Kinetico - Quality Water of Middle Tennessee',
        },
        referredFrom: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Gabriel Simmons', phoneNumber: '790-146-7171' },
        referredTo: { id: '7xnIux4M', name: 'Kinetico - Maricopa Water' },
        referredFrom: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Zoey King', phoneNumber: '712-351-1113' },
        referredTo: {
          id: 'GnR8ncsA',
          name: 'Kinetico - Oxley Softwater Co.',
        },
        referredFrom: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Anthony Morgan', phoneNumber: '118-681-8654' },
        referredTo: {
          id: '1aVBbkq7',
          name: 'Kinetico Quality Water Systems',
        },
        referredFrom: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Penelope Hayes', phoneNumber: '507-693-3149' },
        referredTo: { id: 'ugMLj5z9', name: 'Gordon Water' },
        referredFrom: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Andrew Cooper', phoneNumber: '211-690-7929' },
        referredTo: { id: 'RwHMBsZ9', name: 'The Water Doctor, Inc.' },
        referredFrom: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Nora Long', phoneNumber: '471-238-6248' },
        referredTo: {
          id: 'cQqg3Oiw',
          name: 'Kinetico Quality Water Systems Of SWFL',
        },
        referredFrom: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: {
          name: 'Christopher Butler',
          phoneNumber: '432-177-9852',
        },
        referredTo: { id: 'GuMi3pux', name: 'Maricopia Water' },
        referredFrom: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Layla Ross', phoneNumber: '262-771-2171' },
        referredTo: { id: 'ToPNZPCD', name: 'Martin Water' },
        referredFrom: {
          id: '9f815627-8c28-4eec-b3e5-c95cc18b0877',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Ethan Johnson', phoneNumber: '781-551-9223' },
        referredTo: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: { id: 'WUFH4VbW', name: 'Mermaid Water Systems' },
        contacted: false,
      },
      {
        client: { name: 'Olivia Smith', phoneNumber: '471-259-9416' },
        referredTo: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: { id: 'OIJBMu7k', name: 'Moses Water Sports' },
        contacted: false,
      },
      {
        client: { name: 'Liam Martinez', phoneNumber: '989-399-6958' },
        referredTo: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: {
          id: 'MPUPthKq',
          name: 'Mid America Water Treatment Inc.',
        },
        contacted: false,
      },
      {
        client: { name: 'Emma Thompson', phoneNumber: '251-604-9434' },
        referredTo: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: { id: 'OGok4U65', name: 'Osby Water' },
        contacted: false,
      },
      {
        client: { name: 'Noah Wilson', phoneNumber: '527-844-7640' },
        referredTo: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: {
          id: 's1TfSF6o',
          name: 'Music Mountain Water Co. Inc.',
        },
        contacted: false,
      },
      {
        client: { name: 'Ava Davis', phoneNumber: '155-513-9801' },
        referredTo: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: { id: '3LqyyhHL', name: 'Oxley Softwater' },
        contacted: false,
      },
      {
        client: { name: 'Oliver Anderson', phoneNumber: '650-982-4802' },
        referredTo: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: { id: 'qBiB0Cd3', name: 'Owens Soft Water' },
        contacted: false,
      },
      {
        client: {
          name: 'Isabella Rodriguez',
          phoneNumber: '528-747-4015',
        },
        referredTo: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: {
          id: 'HtsB7HW3',
          name: 'Peacock Water Conditioning',
        },
        contacted: false,
      },
      {
        client: { name: 'Lucas Moore', phoneNumber: '424-943-4164' },
        referredTo: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: {
          id: 'POfSdmXp',
          name: 'Perkin Elmer - Water Testing Company',
        },
        contacted: false,
      },
      {
        client: { name: 'Sophia Turner', phoneNumber: '850-941-9992' },
        referredTo: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: { id: 'MKqjfWio', name: 'Pure Water Components' },
        contacted: false,
      },
      {
        client: { name: 'Mason Clark', phoneNumber: '470-600-9130' },
        referredTo: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: { id: 'bUehkpTl', name: 'Perfect Water' },
        contacted: false,
      },
      {
        client: { name: 'Mia Lewis', phoneNumber: '189-275-6051' },
        referredTo: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: {
          id: 'hDJZuM7X',
          name: 'PHSI - Pure Water Technology',
        },
        contacted: false,
      },
      {
        client: { name: 'Benjamin White', phoneNumber: '887-214-4293' },
        referredTo: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: {
          id: 'O7Fwl2gm',
          name: 'Pure Water Solutions Inc.',
        },
        contacted: false,
      },
      {
        client: { name: 'Charlotte Hill', phoneNumber: '493-625-9488' },
        referredTo: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: { id: 'qYTZu8rx', name: 'Pure Water Concepts LLC' },
        contacted: false,
      },
      {
        client: { name: 'Henry Scott', phoneNumber: '236-196-2126' },
        referredTo: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: { id: 'vP1ECvK7', name: 'Rabb Water Systems' },
        contacted: false,
      },
      {
        client: { name: 'Amelia Walker', phoneNumber: '504-576-2827' },
        referredTo: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: { id: 'p1OyOZdv', name: 'Rushing Water Lodge' },
        contacted: false,
      },
      {
        client: { name: 'Alexander Young', phoneNumber: '157-460-6103' },
        referredTo: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: { id: 'Uy6Pol2q', name: 'Rim Country Water' },
        contacted: false,
      },
      {
        client: { name: 'Harper Adams', phoneNumber: '695-146-1407' },
        referredTo: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: { id: 'ug83zt1n', name: 'Shelton Water' },
        contacted: false,
      },
      {
        client: { name: 'William Mitchell', phoneNumber: '476-122-7687' },
        referredTo: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: {
          id: '808SVkMG',
          name: 'Southwest Water Treatment',
        },
        contacted: false,
      },
      {
        client: { name: 'Evelyn Rivera', phoneNumber: '305-538-3762' },
        referredTo: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        referredFrom: {
          id: 'aBjDP8pn',
          name: 'Shiloh Water Systems Inc.',
        },
        contacted: false,
      },
      {
        client: { name: 'James Carter', phoneNumber: '909-368-7476' },
        referredTo: {
          id: 'LgVL0bym',
          name: 'Random Water Company eBGTMnC7',
        },
        referredFrom: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Abigail Reed', phoneNumber: '365-217-2757' },
        referredTo: {
          id: 'kFjrEvg6',
          name: 'Random Water Company c1Afal3w',
        },
        referredFrom: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Michael Wright', phoneNumber: '762-130-9453' },
        referredTo: {
          id: 'zUNNjOUI',
          name: 'Random Water Company 4xmzVWY8',
        },
        referredFrom: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Emily Coleman', phoneNumber: '968-924-5251' },
        referredTo: {
          id: 'WbLUpKaQ',
          name: 'Random Water Company triCtf0r',
        },
        referredFrom: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Daniel Bell', phoneNumber: '158-750-5019' },
        referredTo: {
          id: 'UA8kCxeF',
          name: 'Random Water Company 1XhRIuVN',
        },
        referredFrom: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Elizabeth Green', phoneNumber: '601-166-5691' },
        referredTo: {
          id: 'cWGa3TxB',
          name: 'Random Water Company lt6gTCoX',
        },
        referredFrom: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Elijah Brooks', phoneNumber: '290-413-9530' },
        referredTo: {
          id: 's9uTQqZy',
          name: 'Random Water Company pK8Uod9O',
        },
        referredFrom: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Sofia Perry', phoneNumber: '343-837-5699' },
        referredTo: {
          id: 'a5P0QxPR',
          name: 'Random Water Company C4g85Ve2',
        },
        referredFrom: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Matthew Cox', phoneNumber: '243-689-4496' },
        referredTo: {
          id: '2ljl1RVa',
          name: 'Random Water Company JYg6uthz',
        },
        referredFrom: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Avery Bailey', phoneNumber: '526-165-1222' },
        referredTo: {
          id: 'KtTuXYzv',
          name: 'Random Water Company pzPSgC0q',
        },
        referredFrom: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'David Reed', phoneNumber: '110-378-5459' },
        referredTo: {
          id: 'L1csKyQI',
          name: 'Random Water Company Y6skc2XC',
        },
        referredFrom: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Ella James', phoneNumber: '169-468-4208' },
        referredTo: {
          id: 'E5YVW9yk',
          name: 'Random Water Company OxkDtadD',
        },
        referredFrom: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: {
          name: 'Jackson Richardson',
          phoneNumber: '254-213-6845',
        },
        referredTo: {
          id: 'qfBXQrrh',
          name: 'Random Water Company xIh7uhEk',
        },
        referredFrom: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Victoria Price', phoneNumber: '974-357-2579' },
        referredTo: {
          id: 'AZdiy9zN',
          name: 'Random Water Company N08LO6LA',
        },
        referredFrom: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Logan Murphy', phoneNumber: '771-563-6530' },
        referredTo: {
          id: '1qAnxZU5',
          name: 'Random Water Company hy3YAPOy',
        },
        referredFrom: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Grace Nelson', phoneNumber: '191-147-8003' },
        referredTo: {
          id: 'CWwHmTS0',
          name: 'Random Water Company KvHKFDQ5',
        },
        referredFrom: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Sebastian Foster', phoneNumber: '137-660-5827' },
        referredTo: {
          id: 'INRksjVZ',
          name: 'Random Water Company hfSMCMYK',
        },
        referredFrom: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Lily Henderson', phoneNumber: '348-867-1737' },
        referredTo: {
          id: 'yQK4kjfQ',
          name: 'Random Water Company dFGdrJwZ',
        },
        referredFrom: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Joseph Ross', phoneNumber: '713-571-5784' },
        referredTo: {
          id: 'MkEWVDgh',
          name: 'Random Water Company 2DkCqxzE',
        },
        referredFrom: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Scarlett Ramirez', phoneNumber: '546-484-5799' },
        referredTo: {
          id: 'InJc8vdH',
          name: 'Random Water Company ngNRgOu6',
        },
        referredFrom: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Samuel Roberts', phoneNumber: '616-470-8721' },
        referredTo: {
          id: 'jQaxZvLl',
          name: 'Random Water Company HG4y8Ezu',
        },
        referredFrom: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Chloe Ward', phoneNumber: '757-943-5004' },
        referredTo: {
          id: 'aPW03VYf',
          name: 'Random Water Company txnv0FNN',
        },
        referredFrom: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Gabriel Simmons', phoneNumber: '196-639-1065' },
        referredTo: {
          id: '7xnIux4M',
          name: 'Random Water Company tsb3mrBH',
        },
        referredFrom: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Zoey King', phoneNumber: '207-563-1178' },
        referredTo: {
          id: 'GnR8ncsA',
          name: 'Random Water Company BJ8BneBA',
        },
        referredFrom: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Anthony Morgan', phoneNumber: '587-441-6656' },
        referredTo: {
          id: '1aVBbkq7',
          name: 'Random Water Company UESONQ6R',
        },
        referredFrom: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Penelope Hayes', phoneNumber: '108-975-8221' },
        referredTo: {
          id: 'ugMLj5z9',
          name: 'Random Water Company cxhTDRxY',
        },
        referredFrom: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Andrew Cooper', phoneNumber: '161-440-7832' },
        referredTo: {
          id: 'RwHMBsZ9',
          name: 'Random Water Company VRiLoi5j',
        },
        referredFrom: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Nora Long', phoneNumber: '222-989-1622' },
        referredTo: {
          id: 'cQqg3Oiw',
          name: 'Random Water Company YKqIO7AN',
        },
        referredFrom: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: {
          name: 'Christopher Butler',
          phoneNumber: '583-324-4120',
        },
        referredTo: {
          id: 'GuMi3pux',
          name: 'Random Water Company yPrjnvkh',
        },
        referredFrom: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
      {
        client: { name: 'Layla Ross', phoneNumber: '237-345-8728' },
        referredTo: {
          id: 'ToPNZPCD',
          name: 'Random Water Company B1OvrrMk',
        },
        referredFrom: {
          id: '4044cfa6-78b0-4db4-8b37-4da885618405',
          name: 'Aqua Clear Water Systems',
        },
        contacted: false,
      },
    ],
    []
  );

  useEffect(() => {
    console.log(company);
    if (refs.results) {
      if (incoming) {
        setReferrals(refs.results.filter((referral) => referral.referredTo.id === company));
      } else {
        setReferrals(refs.results.filter((referral) => referral.referredFrom.id === company));
      }
    } else {
      // eslint-disable-next-line no-lonely-if
      if (incoming) {
        setReferrals(
          fakeData.filter(
            (referral) =>
              referral.referredTo.id === company || referral.referredTo.id === '9f815627-8c28-4eec-b3e5-c95cc18b0877'
          )
        );
      } else {
        setReferrals(
          fakeData.filter(
            (referral) =>
              referral.referredFrom.id === company ||
              referral.referredFrom.id === '9f815627-8c28-4eec-b3e5-c95cc18b0877'
          )
        );
      }
    }
  }, [refs, incoming, company, fakeData]);

  const updateContacted = (event, id, contacted) => {
    console.log('updateContacted', id, contacted);
  };

  const toOrFrom = incoming ? 'Referral From' : 'Referral To';
  const TABLE_HEAD = [
    { id: 'name', label: 'Name', alignRight: false },
    { id: 'phone', label: 'Phone', alignRight: false },
    { id: 'referral', label: toOrFrom, alignRight: false },
    { id: 'contacted', label: 'Contacted', alignRight: false },
  ];

  return (
    <div>
      <h1>Referrals {incoming ? 'Incoming' : 'Outgoing'}</h1>
      <Card sx={{ marginTop: '3%', marginBottom: '3%', padding: '3%' }}>
        {/* {loading ? (
            <Box sx={{ width: '100%' }}>
              <LinearProgress />
            </Box>
          ) : null} */}
        <Scrollbar>
          <TableContainer sx={{ minWidth: 800 }}>
            <Table>
              <ReferralListHead headLabel={TABLE_HEAD} />
              <TableBody>
                {referrals.map((row) => {
                  const { client, referredFrom, referredTo, id } = row;
                  const { name, phoneNumber } = client;
                  const { name: referredFromName } = referredFrom;
                  const { name: referredToName } = referredTo;
                  const contacted = false;
                  return (
                    <TableRow hover key={id} tabIndex={-1}>
                      <TableCell component="th" scope="row" padding="none">
                        <Stack direction="row" alignItems="center" spacing={2}>
                          <Typography variant="subtitle2" noWrap>
                            {name}
                          </Typography>
                        </Stack>
                      </TableCell>
                      <TableCell align="left">{phoneNumber}</TableCell>
                      <TableCell align="left">{incoming ? referredFromName : referredToName}</TableCell>
                      <TableCell>
                        {(() => {
                          if (contacted) {
                            return (
                              <IconButton
                                color="success"
                                aria-label="View/Edit Note"
                                component="label"
                                onClick={(event) => updateContacted(event, id, false)}
                              >
                                <Iconify icon="bi:check-lg" />
                              </IconButton>
                            );
                          }
                          return (
                            <IconButton
                              color="error"
                              aria-label="View/Edit Note"
                              component="label"
                              onClick={(event) => updateContacted(event, id, true)}
                            >
                              <Iconify icon="ps:check-box-empty" />
                            </IconButton>
                          );
                        })()}
                      </TableCell>
                    </TableRow>
                  );
                })}
                {emptyRows > 0 && (
                  <TableRow style={{ height: 53 * emptyRows }}>
                    <TableCell colSpan={2} />
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Scrollbar>
      </Card>
    </div>
  );
};

ReferralsData.propTypes = {
  refs: PropTypes.object.isRequired,
  company: PropTypes.number.isRequired,
  incoming: PropTypes.bool.isRequired,
};

export default ReferralsData;
