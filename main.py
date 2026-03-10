{
    "name": "Integration Google Sheets, OpenAI (ChatGPT, Sora, DALL-E, Whisper)",
    "flow": [
        {
            "id": 1,
            "module": "google-sheets:filterRows",
            "version": 2,
            "parameters": {
                "__IMTCONN__": 7739710
            },
            "mapper": {
                "from": "drive",
                "limit": "5",
                "filter": [
                    [
                        {
                            "a": "D",
                            "b": "pendiente",
                            "o": "text:equal"
                        }
                    ]
                ],
                "sheetId": "Hoja 1",
                "sortOrder": "asc",
                "spreadsheetId": "1h8RyVWn87dx53-FKhYol6QvpYt51ZFfaWUDFgd3ur0U",
                "tableFirstRow": "A1:CZ1",
                "includesHeaders": true,
                "valueRenderOption": "FORMATTED_VALUE",
                "dateTimeRenderOption": "FORMATTED_STRING"
            },
            "metadata": {
                "designer": {
                    "x": 0,
                    "y": 0
                },
                "restore": {
                    "expect": {
                        "from": {
                            "label": "Select from My Drive"
                        },
                        "orderBy": {
                            "mode": "chose"
                        },
                        "sheetId": {
                            "mode": "chose",
                            "label": "Hoja 1"
                        },
                        "sortOrder": {
                            "mode": "chose",
                            "label": "Ascending"
                        },
                        "spreadsheetId": {
                            "mode": "chose",
                            "label": "Reglas Invisibles - Estrategia Contenido"
                        },
                        "tableFirstRow": {
                            "label": "A-CZ"
                        },
                        "includesHeaders": {
                            "mode": "chose",
                            "label": "Yes"
                        },
                        "valueRenderOption": {
                            "mode": "chose",
                            "label": "Formatted value"
                        },
                        "dateTimeRenderOption": {
                            "mode": "chose",
                            "label": "Formatted string"
                        }
                    },
                    "parameters": {
                        "__IMTCONN__": {
                            "data": {
                                "scoped": "true",
                                "connection": "google"
                            },
                            "label": "My Google connection (faithinthelion@gmail.com)"
                        }
                    }
                },
                "parameters": [
                    {
                        "name": "__IMTCONN__",
                        "type": "account:google",
                        "label": "Connection",
                        "required": true
                    }
                ],
                "expect": [
                    {
                        "name": "from",
                        "type": "select",
                        "label": "Search Method",
                        "required": true,
                        "validate": {
                            "enum": [
                                "drive",
                                "share"
                            ]
                        }
                    },
                    {
                        "name": "valueRenderOption",
                        "type": "select",
                        "label": "Value render option",
                        "validate": {
                            "enum": [
                                "FORMATTED_VALUE",
                                "UNFORMATTED_VALUE",
                                "FORMULA"
                            ]
                        }
                    },
                    {
                        "name": "dateTimeRenderOption",
                        "type": "select",
                        "label": "Date and time render option",
                        "validate": {
                            "enum": [
                                "SERIAL_NUMBER",
                                "FORMATTED_STRING"
                            ]
                        }
                    },
                    {
                        "name": "limit",
                        "type": "uinteger",
                        "label": "Limit"
                    },
                    {
                        "name": "spreadsheetId",
                        "type": "select",
                        "label": "Spreadsheet Name",
                        "required": true
                    },
                    {
                        "name": "sheetId",
                        "type": "select",
                        "label": "Sheet Name",
                        "required": true
                    },
                    {
                        "name": "includesHeaders",
                        "type": "select",
                        "label": "Table contains headers",
                        "required": true,
                        "validate": {
                            "enum": [
                                true,
                                false
                            ]
                        }
                    },
                    {
                        "name": "tableFirstRow",
                        "type": "select",
                        "label": "Column range",
                        "required": true,
                        "validate": {
                            "enum": [
                                "A1:Z1",
                                "A1:BZ1",
                                "A1:CZ1",
                                "A1:DZ1",
                                "A1:MZ1",
                                "A1:ZZ1",
                                "A1:AZZ1",
                                "A1:BZZ1",
                                "A1:CZZ1",
                                "A1:DZZ1",
                                "A1:MZZ1",
                                "A1:ZZZ1"
                            ]
                        }
                    },
                    {
                        "name": "filter",
                        "type": "filter",
                        "label": "Filter",
                        "options": "rpc://google-sheets/2/rpcGetFilterKeys?includesHeaders=true"
                    },
                    {
                        "name": "orderBy",
                        "type": "select",
                        "label": "Order by"
                    },
                    {
                        "name": "sortOrder",
                        "type": "select",
                        "label": "Sort order",
                        "validate": {
                            "enum": [
                                "asc",
                                "desc"
                            ]
                        }
                    }
                ],
                "interface": [
                    {
                        "name": "__IMTLENGTH__",
                        "type": "uinteger",
                        "label": "Total number of bundles"
                    },
                    {
                        "name": "__IMTINDEX__",
                        "type": "uinteger",
                        "label": "Bundle order position"
                    },
                    {
                        "name": "__ROW_NUMBER__",
                        "type": "number",
                        "label": "Row number"
                    },
                    {
                        "name": "__SPREADSHEET_ID__",
                        "type": "text",
                        "label": "Spreadsheet ID"
                    },
                    {
                        "name": "__SHEET__",
                        "type": "text",
                        "label": "Sheet"
                    },
                    {
                        "name": "0",
                        "type": "text",
                        "label": "id (A)"
                    },
                    {
                        "name": "1",
                        "type": "text",
                        "label": "tema (B)"
                    },
                    {
                        "name": "2",
                        "type": "text",
                        "label": "hook (C)"
                    },
                    {
                        "name": "3",
                        "type": "text",
                        "label": "estado (D)"
                    },
                    {
                        "name": "4",
                        "type": "text",
                        "label": "guion (E)"
                    },
                    {
                        "name": "5",
                        "type": "text",
                        "label": "audio_url (F)"
                    },
                    {
                        "name": "6",
                        "type": "text",
                        "label": "video_url (G)"
                    },
                    {
                        "name": "7",
                        "type": "text",
                        "label": "titulo_youtube (H)"
                    },
                    {
                        "name": "8",
                        "type": "text",
                        "label": "desc_youtube (I)"
                    },
                    {
                        "name": "9",
                        "type": "text",
                        "label": "desc_tiktok (J)"
                    },
                    {
                        "name": "10",
                        "type": "text",
                        "label": "desc_instagram (K)"
                    },
                    {
                        "name": "11",
                        "type": "text",
                        "label": "desc_facebook (L)"
                    },
                    {
                        "name": "12",
                        "type": "text",
                        "label": "hashtags (M)"
                    },
                    {
                        "name": "13",
                        "type": "text",
                        "label": "(N)"
                    },
                    {
                        "name": "14",
                        "type": "text",
                        "label": "(O)"
                    },
                    {
                        "name": "15",
                        "type": "text",
                        "label": "(P)"
                    },
                    {
                        "name": "16",
                        "type": "text",
                        "label": "(Q)"
                    },
                    {
                        "name": "17",
                        "type": "text",
                        "label": "(R)"
                    },
                    {
                        "name": "18",
                        "type": "text",
                        "label": "(S)"
                    },
                    {
                        "name": "19",
                        "type": "text",
                        "label": "(T)"
                    },
                    {
                        "name": "20",
                        "type": "text",
                        "label": "(U)"
                    },
                    {
                        "name": "21",
                        "type": "text",
                        "label": "(V)"
                    },
                    {
                        "name": "22",
                        "type": "text",
                        "label": "(W)"
                    },
                    {
                        "name": "23",
                        "type": "text",
                        "label": "(X)"
                    },
                    {
                        "name": "24",
                        "type": "text",
                        "label": "(Y)"
                    },
                    {
                        "name": "25",
                        "type": "text",
                        "label": "(Z)"
                    },
                    {
                        "name": "26",
                        "type": "text",
                        "label": "(AA)"
                    },
                    {
                        "name": "27",
                        "type": "text",
                        "label": "(AB)"
                    },
                    {
                        "name": "28",
                        "type": "text",
                        "label": "(AC)"
                    },
                    {
                        "name": "29",
                        "type": "text",
                        "label": "(AD)"
                    },
                    {
                        "name": "30",
                        "type": "text",
                        "label": "(AE)"
                    },
                    {
                        "name": "31",
                        "type": "text",
                        "label": "(AF)"
                    },
                    {
                        "name": "32",
                        "type": "text",
                        "label": "(AG)"
                    },
                    {
                        "name": "33",
                        "type": "text",
                        "label": "(AH)"
                    },
                    {
                        "name": "34",
                        "type": "text",
                        "label": "(AI)"
                    },
                    {
                        "name": "35",
                        "type": "text",
                        "label": "(AJ)"
                    },
                    {
                        "name": "36",
                        "type": "text",
                        "label": "(AK)"
                    },
                    {
                        "name": "37",
                        "type": "text",
                        "label": "(AL)"
                    },
                    {
                        "name": "38",
                        "type": "text",
                        "label": "(AM)"
                    },
                    {
                        "name": "39",
                        "type": "text",
                        "label": "(AN)"
                    },
                    {
                        "name": "40",
                        "type": "text",
                        "label": "(AO)"
                    },
                    {
                        "name": "41",
                        "type": "text",
                        "label": "(AP)"
                    },
                    {
                        "name": "42",
                        "type": "text",
                        "label": "(AQ)"
                    },
                    {
                        "name": "43",
                        "type": "text",
                        "label": "(AR)"
                    },
                    {
                        "name": "44",
                        "type": "text",
                        "label": "(AS)"
                    },
                    {
                        "name": "45",
                        "type": "text",
                        "label": "(AT)"
                    },
                    {
                        "name": "46",
                        "type": "text",
                        "label": "(AU)"
                    },
                    {
                        "name": "47",
                        "type": "text",
                        "label": "(AV)"
                    },
                    {
                        "name": "48",
                        "type": "text",
                        "label": "(AW)"
                    },
                    {
                        "name": "49",
                        "type": "text",
                        "label": "(AX)"
                    },
                    {
                        "name": "50",
                        "type": "text",
                        "label": "(AY)"
                    },
                    {
                        "name": "51",
                        "type": "text",
                        "label": "(AZ)"
                    },
                    {
                        "name": "52",
                        "type": "text",
                        "label": "(BA)"
                    },
                    {
                        "name": "53",
                        "type": "text",
                        "label": "(BB)"
                    },
                    {
                        "name": "54",
                        "type": "text",
                        "label": "(BC)"
                    },
                    {
                        "name": "55",
                        "type": "text",
                        "label": "(BD)"
                    },
                    {
                        "name": "56",
                        "type": "text",
                        "label": "(BE)"
                    },
                    {
                        "name": "57",
                        "type": "text",
                        "label": "(BF)"
                    },
                    {
                        "name": "58",
                        "type": "text",
                        "label": "(BG)"
                    },
                    {
                        "name": "59",
                        "type": "text",
                        "label": "(BH)"
                    },
                    {
                        "name": "60",
                        "type": "text",
                        "label": "(BI)"
                    },
                    {
                        "name": "61",
                        "type": "text",
                        "label": "(BJ)"
                    },
                    {
                        "name": "62",
                        "type": "text",
                        "label": "(BK)"
                    },
                    {
                        "name": "63",
                        "type": "text",
                        "label": "(BL)"
                    },
                    {
                        "name": "64",
                        "type": "text",
                        "label": "(BM)"
                    },
                    {
                        "name": "65",
                        "type": "text",
                        "label": "(BN)"
                    },
                    {
                        "name": "66",
                        "type": "text",
                        "label": "(BO)"
                    },
                    {
                        "name": "67",
                        "type": "text",
                        "label": "(BP)"
                    },
                    {
                        "name": "68",
                        "type": "text",
                        "label": "(BQ)"
                    },
                    {
                        "name": "69",
                        "type": "text",
                        "label": "(BR)"
                    },
                    {
                        "name": "70",
                        "type": "text",
                        "label": "(BS)"
                    },
                    {
                        "name": "71",
                        "type": "text",
                        "label": "(BT)"
                    },
                    {
                        "name": "72",
                        "type": "text",
                        "label": "(BU)"
                    },
                    {
                        "name": "73",
                        "type": "text",
                        "label": "(BV)"
                    },
                    {
                        "name": "74",
                        "type": "text",
                        "label": "(BW)"
                    },
                    {
                        "name": "75",
                        "type": "text",
                        "label": "(BX)"
                    },
                    {
                        "name": "76",
                        "type": "text",
                        "label": "(BY)"
                    },
                    {
                        "name": "77",
                        "type": "text",
                        "label": "(BZ)"
                    },
                    {
                        "name": "78",
                        "type": "text",
                        "label": "(CA)"
                    },
                    {
                        "name": "79",
                        "type": "text",
                        "label": "(CB)"
                    },
                    {
                        "name": "80",
                        "type": "text",
                        "label": "(CC)"
                    },
                    {
                        "name": "81",
                        "type": "text",
                        "label": "(CD)"
                    },
                    {
                        "name": "82",
                        "type": "text",
                        "label": "(CE)"
                    },
                    {
                        "name": "83",
                        "type": "text",
                        "label": "(CF)"
                    },
                    {
                        "name": "84",
                        "type": "text",
                        "label": "(CG)"
                    },
                    {
                        "name": "85",
                        "type": "text",
                        "label": "(CH)"
                    },
                    {
                        "name": "86",
                        "type": "text",
                        "label": "(CI)"
                    },
                    {
                        "name": "87",
                        "type": "text",
                        "label": "(CJ)"
                    },
                    {
                        "name": "88",
                        "type": "text",
                        "label": "(CK)"
                    },
                    {
                        "name": "89",
                        "type": "text",
                        "label": "(CL)"
                    },
                    {
                        "name": "90",
                        "type": "text",
                        "label": "(CM)"
                    },
                    {
                        "name": "91",
                        "type": "text",
                        "label": "(CN)"
                    },
                    {
                        "name": "92",
                        "type": "text",
                        "label": "(CO)"
                    },
                    {
                        "name": "93",
                        "type": "text",
                        "label": "(CP)"
                    },
                    {
                        "name": "94",
                        "type": "text",
                        "label": "(CQ)"
                    },
                    {
                        "name": "95",
                        "type": "text",
                        "label": "(CR)"
                    },
                    {
                        "name": "96",
                        "type": "text",
                        "label": "(CS)"
                    },
                    {
                        "name": "97",
                        "type": "text",
                        "label": "(CT)"
                    },
                    {
                        "name": "98",
                        "type": "text",
                        "label": "(CU)"
                    },
                    {
                        "name": "99",
                        "type": "text",
                        "label": "(CV)"
                    },
                    {
                        "name": "100",
                        "type": "text",
                        "label": "(CW)"
                    },
                    {
                        "name": "101",
                        "type": "text",
                        "label": "(CX)"
                    },
                    {
                        "name": "102",
                        "type": "text",
                        "label": "(CY)"
                    },
                    {
                        "name": "103",
                        "type": "text",
                        "label": "(CZ)"
                    }
                ]
            }
        },
        {
            "id": 20,
            "module": "google-sheets:updateRow",
            "version": 2,
            "parameters": {
                "__IMTCONN__": 7739710
            },
            "mapper": {
                "from": "drive",
                "mode": "select",
                "values": {
                    "3": "procesando"
                },
                "sheetId": "Hoja 1",
                "rowNumber": "{{1.`__ROW_NUMBER__`}}",
                "spreadsheetId": "/1h8RyVWn87dx53-FKhYol6QvpYt51ZFfaWUDFgd3ur0U",
                "includesHeaders": true,
                "useColumnHeaders": false,
                "valueInputOption": "USER_ENTERED"
            },
            "metadata": {
                "designer": {
                    "x": 300,
                    "y": 0
                },
                "restore": {
                    "expect": {
                        "from": {
                            "label": "My Drive"
                        },
                        "mode": {
                            "label": "Search by path"
                        },
                        "sheetId": {
                            "label": "Hoja 1"
                        },
                        "spreadsheetId": {
                            "path": [
                                "Reglas Invisibles - Estrategia Contenido"
                            ]
                        },
                        "includesHeaders": {
                            "label": "Yes"
                        },
                        "useColumnHeaders": {
                            "label": "No",
                            "nested": [
                                {
                                    "name": "values",
                                    "spec": [
                                        {
                                            "name": "0",
                                            "type": "text",
                                            "label": "id (A)"
                                        },
                                        {
                                            "name": "1",
                                            "type": "text",
                                            "label": "tema (B)"
                                        },
                                        {
                                            "name": "2",
                                            "type": "text",
                                            "label": "hook (C)"
                                        },
                                        {
                                            "name": "3",
                                            "type": "text",
                                            "label": "estado (D)"
                                        },
                                        {
                                            "name": "4",
                                            "type": "text",
                                            "label": "guion (E)"
                                        },
                                        {
                                            "name": "5",
                                            "type": "text",
                                            "label": "audio_url (F)"
                                        },
                                        {
                                            "name": "6",
                                            "type": "text",
                                            "label": "video_url (G)"
                                        },
                                        {
                                            "name": "7",
                                            "type": "text",
                                            "label": "titulo_youtube (H)"
                                        },
                                        {
                                            "name": "8",
                                            "type": "text",
                                            "label": "desc_youtube (I)"
                                        },
                                        {
                                            "name": "9",
                                            "type": "text",
                                            "label": "desc_tiktok (J)"
                                        },
                                        {
                                            "name": "10",
                                            "type": "text",
                                            "label": "desc_instagram (K)"
                                        },
                                        {
                                            "name": "11",
                                            "type": "text",
                                            "label": "desc_facebook (L)"
                                        },
                                        {
                                            "name": "12",
                                            "type": "text",
                                            "label": "hashtags (M)"
                                        },
                                        {
                                            "name": "13",
                                            "type": "text",
                                            "label": "(N)"
                                        },
                                        {
                                            "name": "14",
                                            "type": "text",
                                            "label": "(O)"
                                        },
                                        {
                                            "name": "15",
                                            "type": "text",
                                            "label": "(P)"
                                        },
                                        {
                                            "name": "16",
                                            "type": "text",
                                            "label": "(Q)"
                                        },
                                        {
                                            "name": "17",
                                            "type": "text",
                                            "label": "(R)"
                                        },
                                        {
                                            "name": "18",
                                            "type": "text",
                                            "label": "(S)"
                                        },
                                        {
                                            "name": "19",
                                            "type": "text",
                                            "label": "(T)"
                                        },
                                        {
                                            "name": "20",
                                            "type": "text",
                                            "label": "(U)"
                                        },
                                        {
                                            "name": "21",
                                            "type": "text",
                                            "label": "(V)"
                                        },
                                        {
                                            "name": "22",
                                            "type": "text",
                                            "label": "(W)"
                                        },
                                        {
                                            "name": "23",
                                            "type": "text",
                                            "label": "(X)"
                                        },
                                        {
                                            "name": "24",
                                            "type": "text",
                                            "label": "(Y)"
                                        },
                                        {
                                            "name": "25",
                                            "type": "text",
                                            "label": "(Z)"
                                        }
                                    ],
                                    "type": "collection",
                                    "label": "Values in columns",
                                    "metadata": [
                                        [
                                            [
                                                "id",
                                                "tema",
                                                "hook",
                                                "estado",
                                                "guion",
                                                "audio_url",
                                                "video_url",
                                                "titulo_youtube",
                                                "desc_youtube",
                                                "desc_tiktok",
                                                "desc_instagram",
                                                "desc_facebook",
                                                "hashtags"
                                            ]
                                        ]
                                    ]
                                }
                            ]
                        },
                        "valueInputOption": {
                            "mode": "chose",
                            "label": "User entered"
                        }
                    },
                    "parameters": {
                        "__IMTCONN__": {
                            "data": {
                                "scoped": "true",
                                "connection": "google"
                            },
                            "label": "My Google connection (faithinthelion@gmail.com)"
                        }
                    }
                },
                "parameters": [
                    {
                        "name": "__IMTCONN__",
                        "type": "account:google",
                        "label": "Connection",
                        "required": true
                    }
                ],
                "expect": [
                    {
                        "name": "mode",
                        "type": "select",
                        "label": "Search Method",
                        "required": true,
                        "validate": {
                            "enum": [
                                "select",
                                "fromAll",
                                "map"
                            ]
                        }
                    },
                    {
                        "name": "valueInputOption",
                        "type": "select",
                        "label": "Value input option",
                        "validate": {
                            "enum": [
                                "USER_ENTERED",
                                "RAW"
                            ]
                        }
                    },
                    {
                        "name": "from",
                        "type": "select",
                        "label": "Drive",
                        "required": true,
                        "validate": {
                            "enum": [
                                "drive",
                                "share",
                                "team"
                            ]
                        }
                    },
                    {
                        "name": "spreadsheetId",
                        "type": "file",
                        "label": "Spreadsheet Name",
                        "required": true
                    },
                    {
                        "name": "sheetId",
                        "type": "select",
                        "label": "Sheet Name",
                        "required": true
                    },
                    {
                        "name": "rowNumber",
                        "type": "uinteger",
                        "label": "Row number",
                        "required": true
                    },
                    {
                        "name": "includesHeaders",
                        "type": "select",
                        "label": "Table contains headers",
                        "required": true,
                        "validate": {
                            "enum": [
                                true,
                                false
                            ]
                        }
                    },
                    {
                        "name": "useColumnHeaders",
                        "type": "select",
                        "label": "Use column headers as IDs of the columns",
                        "required": true,
                        "validate": {
                            "enum": [
                                true,
                                false
                            ]
                        }
                    },
                    {
                        "name": "values",
                        "spec": [
                            {
                                "name": "0",
                                "type": "text",
                                "label": "id (A)"
                            },
                            {
                                "name": "1",
                                "type": "text",
                                "label": "tema (B)"
                            },
                            {
                                "name": "2",
                                "type": "text",
                                "label": "hook (C)"
                            },
                            {
                                "name": "3",
                                "type": "text",
                                "label": "estado (D)"
                            },
                            {
                                "name": "4",
                                "type": "text",
                                "label": "guion (E)"
                            },
                            {
                                "name": "5",
                                "type": "text",
                                "label": "audio_url (F)"
                            },
                            {
                                "name": "6",
                                "type": "text",
                                "label": "video_url (G)"
                            },
                            {
                                "name": "7",
                                "type": "text",
                                "label": "titulo_youtube (H)"
                            },
                            {
                                "name": "8",
                                "type": "text",
                                "label": "desc_youtube (I)"
                            },
                            {
                                "name": "9",
                                "type": "text",
                                "label": "desc_tiktok (J)"
                            },
                            {
                                "name": "10",
                                "type": "text",
                                "label": "desc_instagram (K)"
                            },
                            {
                                "name": "11",
                                "type": "text",
                                "label": "desc_facebook (L)"
                            },
                            {
                                "name": "12",
                                "type": "text",
                                "label": "hashtags (M)"
                            },
                            {
                                "name": "13",
                                "type": "text",
                                "label": "(N)"
                            },
                            {
                                "name": "14",
                                "type": "text",
                                "label": "(O)"
                            },
                            {
                                "name": "15",
                                "type": "text",
                                "label": "(P)"
                            },
                            {
                                "name": "16",
                                "type": "text",
                                "label": "(Q)"
                            },
                            {
                                "name": "17",
                                "type": "text",
                                "label": "(R)"
                            },
                            {
                                "name": "18",
                                "type": "text",
                                "label": "(S)"
                            },
                            {
                                "name": "19",
                                "type": "text",
                                "label": "(T)"
                            },
                            {
                                "name": "20",
                                "type": "text",
                                "label": "(U)"
                            },
                            {
                                "name": "21",
                                "type": "text",
                                "label": "(V)"
                            },
                            {
                                "name": "22",
                                "type": "text",
                                "label": "(W)"
                            },
                            {
                                "name": "23",
                                "type": "text",
                                "label": "(X)"
                            },
                            {
                                "name": "24",
                                "type": "text",
                                "label": "(Y)"
                            },
                            {
                                "name": "25",
                                "type": "text",
                                "label": "(Z)"
                            }
                        ],
                        "type": "collection",
                        "label": "Values in columns",
                        "metadata": [
                            [
                                [
                                    "id",
                                    "tema",
                                    "hook",
                                    "estado",
                                    "guion",
                                    "audio_url",
                                    "video_url",
                                    "titulo_youtube",
                                    "desc_youtube",
                                    "desc_tiktok",
                                    "desc_instagram",
                                    "desc_facebook",
                                    "hashtags"
                                ]
                            ]
                        ]
                    }
                ]
            }
        },
        {
            "id": 2,
            "module": "openai-gpt-3:askAnything",
            "version": 1,
            "parameters": {},
            "mapper": {
                "model": "gpt-5.2",
                "textPrompt": "Actúa como estratega senior en contenido viral táctico sobre poder real en oficina.\r\n\r\nTu misión es escribir un guion claro, realista, socialmente inteligente y diseñado para generar tensión y comentarios.\r\n\r\nMarca: Reglas Invisibles\r\nFormato: Serie numerada\r\nDuración: 30 segundos\r\nTono: frío, directo\r\nAudiencia: profesionales corporativos\r\n\r\nOBJETIVO DEL VIDEO\r\n\r\n• retención alta\r\n• guardados altos\r\n• generar discusión en comentarios\r\n• reforzar autoridad del canal\r\n\r\nEl guion debe entenderse en una sola lectura rápida.\r\nSi alguien tiene que pensar, está mal escrito.\r\n\r\nDebe sonar:\r\n\r\n• real\r\n• profesional\r\n• socialmente inteligente\r\n• no confrontativo\r\n• no infantil\r\n\r\nNunca exagerado.\r\n\r\nINPUTS DEL VIDEO\r\n\r\nRegla: {{1.`0`}}\r\nTema: {{1.`1`}}\r\nHook base: {{1.`2`}}\n\nSi alguno de estos campos está vacío o contiene texto incompleto, devuelve exactamente:\r\n\r\nERROR_INPUTS_INCOMPLETOS\r\n\r\nNo intentes completar información.\r\nNo pidas datos adicionales.\r\n\r\nREGLA CENTRAL\r\n\r\nCada bloque debe incluir:\r\n\r\n• acción visible\r\n• consecuencia visible\r\n• impacto profesional claro\r\n\r\nNada interno.\r\nNada abstracto.\r\n\r\nPROHIBIDO\r\n\r\n• frases largas\r\n• dos ideas en una línea\r\n• verbos ambiguos\r\n• teoría psicológica\r\n• acusaciones directas\r\n• acciones inmaduras\r\n• confrontación abierta\r\n• numeración\r\n• listas\r\n• viñetas\r\n\r\nSi una frase suena poco realista en una oficina, reescribir.\r\n\r\nESTRUCTURA OBLIGATORIA\r\n\r\nHOOK\r\n\r\nDebe mantener formato:\r\n\r\nSi X pasa, Y pasa.\r\n\r\nDebe mostrar una micro-situación visible de oficina.\r\nDebe implicar pérdida profesional.\r\n\r\nESCENA\r\n\r\n3–4 líneas.\r\n\r\nSolo acciones visibles.\r\nDebe parecer una escena real de reunión.\r\n\r\nESCALADA\r\n\r\nMostrar pérdida pública visible inmediata.\r\n\r\nEjemplos:\r\n\r\n• otro responde por ti\r\n• el jefe decide mirando a otro\r\n• tu idea queda fuera\r\n• otro recibe el crédito\r\n\r\nEXPLICACIÓN\r\n\r\nMáximo 2 líneas.\r\n\r\nSolo hechos observables.\r\n\r\nINSERCIÓN DEL MANUAL\r\n\r\nDebe aparecer exactamente este texto:\r\n\r\nEstas son reglas que casi nadie explica. Varias están en un manual gratis. El link está en el perfil.\r\n\r\nNo modificar.\r\nNo resumir.\r\nNo mover.\r\n\r\nFRASE DE FRICCIÓN\r\n\r\nDebe romper una creencia común.\r\nDebe generar discusión.\r\nNo emocional.\r\n\r\nACCIÓN ESTRATÉGICA\r\n\r\nDebe incluir:\r\n\r\n1. qué hacer en el momento\r\n2. cómo decirlo en la reunión\r\n3. qué efecto produce en el equipo\r\n\r\nDebe tener entre 3 y 5 líneas.\r\nDebe sonar profesional.\r\n\r\nProhibido acusar o confrontar.\r\n\r\nFRASE DOMINANTE\r\n\r\nFormato:\r\n\r\nSi X pasa, Y pasa.\r\n\r\n7–12 palabras.\r\n\r\nDebe sonar como regla profesional repetible.\r\n\r\nLÍNEA DIVISIVA\r\n\r\nDebe dividir al público en dos perfiles profesionales.\r\n\r\nCIERRE\r\n\r\nDebe terminar exactamente con:\r\n\r\nEsta es la Regla Invisible #{{1.`0`}}.\r\n\r\nCONTROL DE DURACIÓN\r\n\r\nEl guion completo debe tener entre 65 y 85 palabras.\r\n\r\nSi supera 85 palabras, recortar.\r\nSi tiene menos de 65, ampliar.\r\n\r\nFORMATO DE SALIDA\r\n\r\nDevuelve SOLO el guion final.\r\n\r\nNo expliques nada.\r\nNo muestres análisis.\r\nNo repitas los inputs.\r\nNo agregues encabezados.\r\nNo agregues títulos.\r\nNo agregues numeración.\r\nNo agregues listas.\r\n\r\nEl texto debe ser plano, limpio y listo para narración."
            },
            "metadata": {
                "designer": {
                    "x": 600,
                    "y": 0
                },
                "restore": {
                    "expect": {
                        "model": {
                            "label": "GPT-5.2The most advanced model with superior reasoning, speed, and instruction-following for complex, real-world tasks"
                        }
                    }
                },
                "expect": [
                    {
                        "name": "model",
                        "type": "select",
                        "label": "Model",
                        "required": true,
                        "validate": {
                            "enum": [
                                "gpt-5.2",
                                "gpt-5.1",
                                "gpt-5",
                                "gpt-5-nano",
                                "gpt-5-mini"
                            ]
                        }
                    },
                    {
                        "name": "textPrompt",
                        "type": "text",
                        "label": "Text prompt",
                        "required": true
                    }
                ]
            }
        },
        {
            "id": 56,
            "module": "openai-gpt-3:askAnything",
            "version": 1,
            "parameters": {},
            "mapper": {
                "model": "gpt-5.4",
                "textPrompt": "Actúa como estratega senior en contenido viral, SEO multiplataforma y growth orgánico para YouTube Shorts, TikTok, Instagram Reels y Facebook Reels.\r\n\r\nTu trabajo es crear títulos, descripciones y hashtags optimizados para descubrimiento algorítmico y engagement.\r\n\r\nDebes utilizar principios de:\r\n\r\nCONTAGIOUS (STEPPS – Jonah Berger)\r\nsocial currency\r\ntriggers\r\nemociones de alta activación\r\nvalor práctico\r\nstorytelling\r\n\r\nHOOKED (Nir Eyal)\r\ntrigger\r\nacción simple\r\nrecompensa variable\r\nmicro-inversión (comentario, guardado, compartir)\r\n\r\nTRACTION (Bullseye Framework)\r\noptimización para discovery channels:\r\nYouTube Shorts\r\nTikTok\r\nInstagram Reels\r\nFacebook Reels\r\n\r\nGROWTH HACKING (Sean Ellis)\r\nmaximizar:\r\ncomentarios\r\nguardados\r\ncompartidos\r\nseguidores\r\nretención\r\n\r\nCONTEXTO DE MARCA\r\n\r\nMarca: Reglas Invisibles  \r\nNicho: Psicología estratégica aplicada al entorno corporativo  \r\nFormato: Serie numerada  \r\nDuración del video: 30–35 segundos  \r\nTono: frío, táctico, dominante  \r\nAudiencia: 22–40 años, empleados y profesionales\r\n\r\nObjetivos del contenido:\r\n\r\nprovocar reflexión incómoda  \r\nactivar comentarios  \r\naumentar guardados  \r\nreforzar identidad profesional  \r\npreparar venta futura del manual digital\r\n\r\nREGLAS DE ESTILO\r\n\r\nNo usar emojis.  \r\nNo sonar motivacional.  \r\nNo usar frases de coach.  \r\nNo escribir párrafos largos.  \r\nNo repetir palabras innecesariamente.\r\n\r\nEl tono debe ser analítico, profesional y ligeramente incómodo.\r\n\r\n────────────────────────\r\n\r\nINFORMACIÓN DEL VIDEO\r\n\r\nNúmero de regla:\r\n{{id}}\r\n\r\nTema del video:\r\n{{tema}}\r\n\r\nHook del video:\r\n{{hook}}\r\n\r\nGuion completo:\r\n{{guion}}\r\n\r\n────────────────────────\r\n\r\nDebes generar:\r\n\r\n1. Título optimizado para YouTube Shorts  \r\n2. Descripción YouTube  \r\n3. Descripción TikTok  \r\n4. Descripción Instagram  \r\n5. Descripción Facebook  \r\n6. Hashtags estratégicos  \r\n7. Comentario fijado\r\n\r\n────────────────────────\r\n\r\nREGLAS PARA CADA ELEMENTO\r\n\r\nTÍTULO YOUTUBE\r\nmáximo 70 caracteres  \r\ndebe generar curiosidad profesional  \r\nno clickbait infantil  \r\nincluir número de regla\r\n\r\nDESCRIPCIÓN YOUTUBE\r\nmáximo 5 líneas\r\n\r\nestructura:\r\nhook fuerte  \r\nexplicación breve  \r\ncontexto laboral  \r\npregunta incómoda  \r\nmención del manual\r\n\r\nDebe incluir naturalmente palabras clave:\r\n\r\npsicología en el trabajo  \r\npolítica de oficina  \r\npoder en la oficina  \r\ndinámicas laborales  \r\nreglas invisibles del trabajo\r\n\r\nDESCRIPCIÓN TIKTOK\r\n\r\nestructura:\r\nfrase de tensión  \r\ncontexto corto  \r\npregunta polarizante  \r\nllamada a guardar\r\n\r\nDESCRIPCIÓN INSTAGRAM\r\n\r\nestructura:\r\nfrase fuerte  \r\nmicro explicación  \r\nreflexión incómoda  \r\npregunta divisiva  \r\nCTA guardar\r\n\r\nDESCRIPCIÓN FACEBOOK\r\n\r\nestructura:\r\nexplicación clara  \r\nejemplo cotidiano  \r\npregunta para debate\r\n\r\nHASHTAGS\r\n\r\nentre 8 y 12  \r\ncombinar SEO profesional + nicho laboral\r\n\r\nNo usar hashtags genéricos como:\r\n#fyp  \r\n#viral\r\n\r\nCOMENTARIO FIJADO\r\n\r\ndebe provocar debate profesional\r\n\r\n────────────────────────\r\n\r\nREGLA CRÍTICA\n\nNo pidas más información.\nNo digas que faltan datos.\nNo expliques nada.\nNo hagas preguntas fuera de los campos solicitados.\nSi algún dato es ambiguo, infiérelo a partir del guion.\n\nTodos los campos del JSON deben contener texto.\nNingún campo puede quedar vacío.\n\nDevuelve EXACTAMENTE este JSON:\r\n\r\n{\r\n\"title_youtube\":\"\",\r\n\"description_youtube\":\"\",\r\n\"description_tiktok\":\"\",\r\n\"description_instagram\":\"\",\r\n\"description_facebook\":\"\",\r\n\"hashtags\":\"\",\r\n\"pinned_comment\":\"\"\r\n}"
            },
            "metadata": {
                "designer": {
                    "x": 900,
                    "y": 0
                },
                "restore": {
                    "expect": {
                        "model": {
                            "label": "GPT-5.4The frontier model for broad, general-purpose work and coding, delivering higher-quality outputs for complex tasks"
                        }
                    }
                },
                "expect": [
                    {
                        "name": "model",
                        "type": "select",
                        "label": "Model",
                        "required": true,
                        "validate": {
                            "enum": [
                                "gpt-5.4",
                                "gpt-5.3-chat-latest",
                                "gpt-5.2",
                                "gpt-5.1",
                                "gpt-5",
                                "gpt-5-nano",
                                "gpt-5-mini"
                            ]
                        }
                    },
                    {
                        "name": "textPrompt",
                        "type": "text",
                        "label": "Text prompt",
                        "required": true
                    }
                ]
            }
        },
        {
            "id": 59,
            "module": "json:ParseJSON",
            "version": 1,
            "parameters": {
                "type": 300058
            },
            "mapper": {
                "json": "{{56.result}}"
            },
            "metadata": {
                "designer": {
                    "x": 1200,
                    "y": 0
                },
                "restore": {
                    "parameters": {
                        "type": {
                            "label": "My data structure"
                        }
                    }
                },
                "parameters": [
                    {
                        "name": "type",
                        "type": "udt",
                        "label": "Data structure"
                    }
                ],
                "expect": [
                    {
                        "name": "json",
                        "type": "text",
                        "label": "JSON string",
                        "required": true
                    }
                ],
                "interface": [
                    {
                        "name": "title_youtube",
                        "label": "Title youtube",
                        "help": "",
                        "type": "text",
                        "default": null,
                        "required": false,
                        "multiline": false
                    },
                    {
                        "name": "description_youtube",
                        "label": "Description youtube",
                        "help": "",
                        "type": "text",
                        "default": null,
                        "required": false,
                        "multiline": false
                    },
                    {
                        "name": "description_tiktok",
                        "label": "Description tiktok",
                        "help": "",
                        "type": "text",
                        "default": null,
                        "required": false,
                        "multiline": false
                    },
                    {
                        "name": "description_instagram",
                        "label": "Description instagram",
                        "help": "",
                        "type": "text",
                        "default": null,
                        "required": false,
                        "multiline": false
                    },
                    {
                        "name": "description_facebook",
                        "label": "Description facebook",
                        "help": "",
                        "type": "text",
                        "default": null,
                        "required": false,
                        "multiline": false
                    },
                    {
                        "name": "hashtags",
                        "label": "Hashtags",
                        "help": "",
                        "type": "text",
                        "default": null,
                        "required": false,
                        "multiline": false
                    },
                    {
                        "name": "pinned_comment",
                        "label": "Pinned comment",
                        "help": "",
                        "type": "text",
                        "default": null,
                        "required": false,
                        "multiline": false
                    }
                ]
            }
        },
        {
            "id": 5,
            "module": "google-sheets:updateRow",
            "version": 2,
            "parameters": {
                "__IMTCONN__": 7739710
            },
            "mapper": {
                "mode": "select",
                "valueInputOption": "USER_ENTERED",
                "from": "drive",
                "spreadsheetId": "/1h8RyVWn87dx53-FKhYol6QvpYt51ZFfaWUDFgd3ur0U",
                "sheetId": "Hoja 1",
                "rowNumber": "{{1.`__ROW_NUMBER__`}}",
                "includesHeaders": true,
                "useColumnHeaders": false,
                "values": {
                    "3": "guion_listo",
                    "4": "{{2.result}}",
                    "7": "{{59.title_youtube}}",
                    "8": "{{59.description_youtube}}",
                    "9": "{{59.description_tiktok}}",
                    "10": "{{59.description_instagram}}",
                    "11": "{{59.description_facebook}}",
                    "12": "{{59.hashtags}}",
                    "13": "{{59.pinned_comment}}"
                }
            },
            "metadata": {
                "designer": {
                    "x": 1500,
                    "y": 0
                },
                "restore": {
                    "parameters": {
                        "__IMTCONN__": {
                            "label": "My Google connection (faithinthelion@gmail.com)",
                            "data": {
                                "scoped": "true",
                                "connection": "google"
                            }
                        }
                    },
                    "expect": {
                        "mode": {
                            "label": "Search by path"
                        },
                        "valueInputOption": {
                            "mode": "chose",
                            "label": "User entered"
                        },
                        "from": {
                            "label": "My Drive"
                        },
                        "spreadsheetId": {
                            "path": [
                                "Reglas Invisibles - Estrategia Contenido"
                            ]
                        },
                        "sheetId": {
                            "label": "Hoja 1"
                        },
                        "includesHeaders": {
                            "label": "Yes"
                        },
                        "useColumnHeaders": {
                            "nested": [
                                {
                                    "name": "values",
                                    "spec": [
                                        {
                                            "name": "0",
                                            "type": "text",
                                            "label": "id (A)"
                                        },
                                        {
                                            "name": "1",
                                            "type": "text",
                                            "label": "tema (B)"
                                        },
                                        {
                                            "name": "2",
                                            "type": "text",
                                            "label": "hook (C)"
                                        },
                                        {
                                            "name": "3",
                                            "type": "text",
                                            "label": "estado (D)"
                                        },
                                        {
                                            "name": "4",
                                            "type": "text",
                                            "label": "guion (E)"
                                        },
                                        {
                                            "name": "5",
                                            "type": "text",
                                            "label": "audio_url (F)"
                                        },
                                        {
                                            "name": "6",
                                            "type": "text",
                                            "label": "video_url (G)"
                                        },
                                        {
                                            "name": "7",
                                            "type": "text",
                                            "label": "titulo_youtube (H)"
                                        },
                                        {
                                            "name": "8",
                                            "type": "text",
                                            "label": "desc_youtube (I)"
                                        },
                                        {
                                            "name": "9",
                                            "type": "text",
                                            "label": "desc_tiktok (J)"
                                        },
                                        {
                                            "name": "10",
                                            "type": "text",
                                            "label": "desc_instagram (K)"
                                        },
                                        {
                                            "name": "11",
                                            "type": "text",
                                            "label": "desc_facebook (L)"
                                        },
                                        {
                                            "name": "12",
                                            "type": "text",
                                            "label": "hashtags (M)"
                                        },
                                        {
                                            "name": "13",
                                            "type": "text",
                                            "label": "(N)"
                                        },
                                        {
                                            "name": "14",
                                            "type": "text",
                                            "label": "(O)"
                                        },
                                        {
                                            "name": "15",
                                            "type": "text",
                                            "label": "(P)"
                                        },
                                        {
                                            "name": "16",
                                            "type": "text",
                                            "label": "(Q)"
                                        },
                                        {
                                            "name": "17",
                                            "type": "text",
                                            "label": "(R)"
                                        },
                                        {
                                            "name": "18",
                                            "type": "text",
                                            "label": "(S)"
                                        },
                                        {
                                            "name": "19",
                                            "type": "text",
                                            "label": "(T)"
                                        },
                                        {
                                            "name": "20",
                                            "type": "text",
                                            "label": "(U)"
                                        },
                                        {
                                            "name": "21",
                                            "type": "text",
                                            "label": "(V)"
                                        },
                                        {
                                            "name": "22",
                                            "type": "text",
                                            "label": "(W)"
                                        },
                                        {
                                            "name": "23",
                                            "type": "text",
                                            "label": "(X)"
                                        },
                                        {
                                            "name": "24",
                                            "type": "text",
                                            "label": "(Y)"
                                        },
                                        {
                                            "name": "25",
                                            "type": "text",
                                            "label": "(Z)"
                                        }
                                    ],
                                    "type": "collection",
                                    "label": "Values in columns",
                                    "metadata": [
                                        [
                                            [
                                                "id",
                                                "tema",
                                                "hook",
                                                "estado",
                                                "guion",
                                                "audio_url",
                                                "video_url",
                                                "titulo_youtube",
                                                "desc_youtube",
                                                "desc_tiktok",
                                                "desc_instagram",
                                                "desc_facebook",
                                                "hashtags"
                                            ]
                                        ]
                                    ]
                                }
                            ],
                            "label": "No"
                        }
                    }
                },
                "parameters": [
                    {
                        "name": "__IMTCONN__",
                        "type": "account:google",
                        "label": "Connection",
                        "required": true
                    }
                ],
                "expect": [
                    {
                        "name": "mode",
                        "type": "select",
                        "label": "Search Method",
                        "required": true,
                        "validate": {
                            "enum": [
                                "select",
                                "fromAll",
                                "map"
                            ]
                        }
                    },
                    {
                        "name": "valueInputOption",
                        "type": "select",
                        "label": "Value input option",
                        "validate": {
                            "enum": [
                                "USER_ENTERED",
                                "RAW"
                            ]
                        }
                    },
                    {
                        "name": "from",
                        "type": "select",
                        "label": "Drive",
                        "required": true,
                        "validate": {
                            "enum": [
                                "drive",
                                "share",
                                "team"
                            ]
                        }
                    },
                    {
                        "name": "spreadsheetId",
                        "type": "file",
                        "label": "Spreadsheet Name",
                        "required": true
                    },
                    {
                        "name": "sheetId",
                        "type": "select",
                        "label": "Sheet Name",
                        "required": true
                    },
                    {
                        "name": "rowNumber",
                        "type": "uinteger",
                        "label": "Row number",
                        "required": true
                    },
                    {
                        "name": "includesHeaders",
                        "type": "select",
                        "label": "Table contains headers",
                        "required": true,
                        "validate": {
                            "enum": [
                                true,
                                false
                            ]
                        }
                    },
                    {
                        "name": "useColumnHeaders",
                        "type": "select",
                        "label": "Use column headers as IDs of the columns",
                        "required": true,
                        "validate": {
                            "enum": [
                                true,
                                false
                            ]
                        }
                    },
                    {
                        "name": "values",
                        "type": "collection",
                        "label": "Values in columns",
                        "metadata": [
                            [
                                [
                                    "id",
                                    "tema",
                                    "hook",
                                    "estado",
                                    "guion",
                                    "audio_url",
                                    "video_url",
                                    "titulo_youtube",
                                    "desc_youtube",
                                    "desc_tiktok",
                                    "desc_instagram",
                                    "desc_facebook",
                                    "hashtags"
                                ]
                            ]
                        ],
                        "spec": [
                            {
                                "name": "0",
                                "type": "text",
                                "label": "id (A)"
                            },
                            {
                                "name": "1",
                                "type": "text",
                                "label": "tema (B)"
                            },
                            {
                                "name": "2",
                                "type": "text",
                                "label": "hook (C)"
                            },
                            {
                                "name": "3",
                                "type": "text",
                                "label": "estado (D)"
                            },
                            {
                                "name": "4",
                                "type": "text",
                                "label": "guion (E)"
                            },
                            {
                                "name": "5",
                                "type": "text",
                                "label": "audio_url (F)"
                            },
                            {
                                "name": "6",
                                "type": "text",
                                "label": "video_url (G)"
                            },
                            {
                                "name": "7",
                                "type": "text",
                                "label": "titulo_youtube (H)"
                            },
                            {
                                "name": "8",
                                "type": "text",
                                "label": "desc_youtube (I)"
                            },
                            {
                                "name": "9",
                                "type": "text",
                                "label": "desc_tiktok (J)"
                            },
                            {
                                "name": "10",
                                "type": "text",
                                "label": "desc_instagram (K)"
                            },
                            {
                                "name": "11",
                                "type": "text",
                                "label": "desc_facebook (L)"
                            },
                            {
                                "name": "12",
                                "type": "text",
                                "label": "hashtags (M)"
                            },
                            {
                                "name": "13",
                                "type": "text",
                                "label": "(N)"
                            },
                            {
                                "name": "14",
                                "type": "text",
                                "label": "(O)"
                            },
                            {
                                "name": "15",
                                "type": "text",
                                "label": "(P)"
                            },
                            {
                                "name": "16",
                                "type": "text",
                                "label": "(Q)"
                            },
                            {
                                "name": "17",
                                "type": "text",
                                "label": "(R)"
                            },
                            {
                                "name": "18",
                                "type": "text",
                                "label": "(S)"
                            },
                            {
                                "name": "19",
                                "type": "text",
                                "label": "(T)"
                            },
                            {
                                "name": "20",
                                "type": "text",
                                "label": "(U)"
                            },
                            {
                                "name": "21",
                                "type": "text",
                                "label": "(V)"
                            },
                            {
                                "name": "22",
                                "type": "text",
                                "label": "(W)"
                            },
                            {
                                "name": "23",
                                "type": "text",
                                "label": "(X)"
                            },
                            {
                                "name": "24",
                                "type": "text",
                                "label": "(Y)"
                            },
                            {
                                "name": "25",
                                "type": "text",
                                "label": "(Z)"
                            }
                        ]
                    }
                ],
                "advanced": true
            }
        },
        {
            "id": 9,
            "module": "http:MakeRequest",
            "version": 4,
            "parameters": {
                "authenticationType": "noAuth",
                "tlsType": "",
                "proxyKeychain": ""
            },
            "mapper": {
                "url": "https://api.elevenlabs.io/v1/text-to-speech/PHKlYg202ODwQRa3Fxuo/with-timestamps",
                "method": "post",
                "headers": [
                    {
                        "name": "xi-api-key",
                        "value": "sk_95fda54480b7ae391854b9289b300d69c139dcb92b373af7"
                    },
                    {
                        "name": "Content-Type",
                        "value": "application/json"
                    },
                    {
                        "name": "Accept",
                        "value": "application/json"
                    }
                ],
                "contentType": "json",
                "parseResponse": true,
                "stopOnHttpError": true,
                "allowRedirects": true,
                "shareCookies": false,
                "requestCompressedContent": true,
                "inputMethod": "dataStructure",
                "bodyDataStructure": 299818,
                "dataStructureBodyContent": {
                    "text": "{{2.result}}",
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {
                        "stability": "0.45",
                        "similarity_boost": "0.75"
                    }
                }
            },
            "metadata": {
                "designer": {
                    "x": 1800,
                    "y": 0
                },
                "restore": {
                    "parameters": {
                        "authenticationType": {
                            "label": "No authenticationUse when no credentials are required for the request."
                        },
                        "tlsType": {
                            "label": "Empty"
                        },
                        "proxyKeychain": {
                            "label": "Choose a key"
                        }
                    },
                    "expect": {
                        "method": {
                            "mode": "chose",
                            "label": "POST"
                        },
                        "headers": {
                            "mode": "chose",
                            "items": [
                                null,
                                null,
                                null
                            ]
                        },
                        "queryParameters": {
                            "mode": "chose"
                        },
                        "contentType": {
                            "label": "application/jsonEnter data in the JSON format, as a string or using a data structure."
                        },
                        "parseResponse": {
                            "mode": "chose"
                        },
                        "stopOnHttpError": {
                            "mode": "chose"
                        },
                        "allowRedirects": {
                            "mode": "chose"
                        },
                        "shareCookies": {
                            "mode": "chose"
                        },
                        "requestCompressedContent": {
                            "mode": "chose"
                        },
                        "inputMethod": {
                            "label": "Data structureDefine the JSON body with a data structure to map or enter values for each key. JSON reserved characters are escaped automatically."
                        },
                        "bodyDataStructure": {
                            "label": "elevenlabs_body"
                        },
                        "paginationType": {
                            "label": "Empty"
                        }
                    }
                },
                "parameters": [
                    {
                        "name": "authenticationType",
                        "type": "select",
                        "label": "Authentication type",
                        "required": true,
                        "validate": {
                            "enum": [
                                "noAuth",
                                "apiKey",
                                "basicAuth",
                                "oAuth"
                            ]
                        }
                    },
                    {
                        "name": "tlsType",
                        "type": "select",
                        "label": "Transport layer security (TLS)",
                        "validate": {
                            "enum": [
                                "mTls",
                                "tls"
                            ]
                        }
                    },
                    {
                        "name": "proxyKeychain",
                        "type": "keychain:proxy",
                        "label": "Proxy"
                    }
                ],
                "expect": [
                    {
                        "name": "url",
                        "type": "url",
                        "label": "URL",
                        "required": true
                    },
                    {
                        "name": "method",
                        "type": "select",
                        "label": "Method",
                        "required": true,
                        "validate": {
                            "enum": [
                                "get",
                                "head",
                                "post",
                                "put",
                                "patch",
                                "delete",
                                "options"
                            ]
                        }
                    },
                    {
                        "name": "headers",
                        "type": "array",
                        "label": "Headers",
                        "spec": {
                            "name": "value",
                            "label": "Header",
                            "type": "collection",
                            "spec": [
                                {
                                    "name": "name",
                                    "label": "Name",
                                    "type": "text",
                                    "required": true,
                                    "validate": {
                                        "pattern": "^[-!#$%&'*+.^_`|~0-9A-Za-z]+$"
                                    }
                                },
                                {
                                    "name": "value",
                                    "label": "Value",
                                    "type": "text"
                                }
                            ]
                        }
                    },
                    {
                        "name": "queryParameters",
                        "type": "array",
                        "label": "Query parameters",
                        "spec": {
                            "name": "value",
                            "label": "Parameter",
                            "type": "collection",
                            "spec": [
                                {
                                    "name": "name",
                                    "label": "Name",
                                    "type": "text",
                                    "required": true
                                },
                                {
                                    "name": "value",
                                    "label": "Value",
                                    "type": "text"
                                }
                            ]
                        }
                    },
                    {
                        "name": "contentType",
                        "type": "select",
                        "label": "Body content type",
                        "validate": {
                            "enum": [
                                "json",
                                "multipart",
                                "urlEncoded",
                                "custom"
                            ]
                        }
                    },
                    {
                        "name": "parseResponse",
                        "type": "boolean",
                        "label": "Parse response",
                        "required": true
                    },
                    {
                        "name": "stopOnHttpError",
                        "type": "boolean",
                        "label": "Return error if HTTP request fails",
                        "required": true
                    },
                    {
                        "name": "timeout",
                        "type": "uinteger",
                        "label": "Timeout",
                        "validate": {
                            "min": 1,
                            "max": 300
                        }
                    },
                    {
                        "name": "allowRedirects",
                        "type": "boolean",
                        "label": "Allow redirects",
                        "required": true
                    },
                    {
                        "name": "shareCookies",
                        "type": "boolean",
                        "label": "Share cookies with other HTTP modules",
                        "required": true
                    },
                    {
                        "name": "requestCompressedContent",
                        "type": "boolean",
                        "label": "Request compressed content",
                        "required": true
                    },
                    {
                        "name": "inputMethod",
                        "type": "select",
                        "label": "Body input method",
                        "required": true,
                        "validate": {
                            "enum": [
                                "dataStructure",
                                "jsonString"
                            ]
                        }
                    },
                    {
                        "name": "bodyDataStructure",
                        "type": "udt",
                        "label": "Body structure",
                        "required": true
                    },
                    {
                        "name": "dataStructureBodyContent",
                        "type": "collection",
                        "label": "Body content",
                        "spec": [
                            {
                                "name": "text",
                                "type": "text",
                                "label": null,
                                "required": true
                            },
                            {
                                "name": "model_id",
                                "type": "text",
                                "label": null,
                                "required": true
                            },
                            {
                                "name": "voice_settings",
                                "type": "collection",
                                "label": null,
                                "spec": [
                                    {
                                        "name": "stability",
                                        "type": "number",
                                        "label": null,
                                        "required": true
                                    },
                                    {
                                        "name": "similarity_boost",
                                        "type": "number",
                                        "label": null,
                                        "required": true
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "name": "paginationType",
                        "type": "select",
                        "label": "Pagination type",
                        "validate": {
                            "enum": [
                                "offsetBased",
                                "pageBased",
                                "urlBased",
                                "tokenBased"
                            ]
                        }
                    }
                ],
                "interface": [
                    {
                        "name": "data",
                        "label": "Data",
                        "type": "any"
                    },
                    {
                        "name": "statusCode",
                        "label": "Status Code",
                        "type": "number"
                    },
                    {
                        "name": "headers",
                        "label": "Headers",
                        "type": "collection",
                        "spec": [
                            {
                                "name": "content-length",
                                "label": "Content-Length",
                                "type": "text"
                            },
                            {
                                "name": "content-encoding",
                                "label": "Content-Encoding",
                                "type": "text"
                            },
                            {
                                "name": "content-type",
                                "label": "Content-Type",
                                "type": "text"
                            },
                            {
                                "name": "server",
                                "label": "Server",
                                "type": "text"
                            },
                            {
                                "name": "cache-control",
                                "label": "Cache-Control",
                                "type": "text"
                            },
                            {
                                "name": "set-cookie",
                                "label": "Set-Cookie",
                                "type": "array",
                                "spec": {
                                    "type": "text"
                                }
                            }
                        ]
                    }
                ]
            }
        },
        {
            "id": 24,
            "module": "http:MakeRequest",
            "version": 4,
            "parameters": {
                "authenticationType": "noAuth",
                "tlsType": "",
                "proxyKeychain": ""
            },
            "mapper": {
                "url": "https://ffmpeg-render-api-production-1143.up.railway.app/render",
                "method": "post",
                "contentType": "json",
                "parseResponse": true,
                "stopOnHttpError": true,
                "allowRedirects": true,
                "shareCookies": false,
                "requestCompressedContent": true,
                "inputMethod": "dataStructure",
                "bodyDataStructure": 301172,
                "dataStructureBodyContent": {
                    "numero_regla": "{{1.`0`}}",
                    "guion": "{{2.result}}",
                    "subtitles_mode": "dynamic",
                    "audio_base64": "{{9.data.audio_base64}}",
                    "normalized_alignment": {
                        "characters": "{{9.data.normalized_alignment.characters}}",
                        "character_start_times_seconds": "{{9.data.normalized_alignment.character_start_times_seconds}}",
                        "character_end_times_seconds": "{{9.data.normalized_alignment.character_end_times_seconds}}"
                    }
                }
            },
            "metadata": {
                "designer": {
                    "x": 2100,
                    "y": 0
                },
                "restore": {
                    "parameters": {
                        "authenticationType": {
                            "label": "No authenticationUse when no credentials are required for the request."
                        },
                        "tlsType": {
                            "label": "Empty"
                        },
                        "proxyKeychain": {
                            "label": "Choose a key"
                        }
                    },
                    "expect": {
                        "method": {
                            "mode": "chose",
                            "label": "POST"
                        },
                        "headers": {
                            "mode": "chose"
                        },
                        "queryParameters": {
                            "mode": "chose",
                            "collapsed": true
                        },
                        "contentType": {
                            "label": "application/jsonEnter data in the JSON format, as a string or using a data structure."
                        },
                        "parseResponse": {
                            "mode": "chose"
                        },
                        "stopOnHttpError": {
                            "mode": "chose"
                        },
                        "allowRedirects": {
                            "mode": "chose"
                        },
                        "shareCookies": {
                            "mode": "chose"
                        },
                        "requestCompressedContent": {
                            "mode": "chose"
                        },
                        "inputMethod": {
                            "label": "Data structureDefine the JSON body with a data structure to map or enter values for each key. JSON reserved characters are escaped automatically."
                        },
                        "bodyDataStructure": {
                            "label": "My data structure"
                        },
                        "dataStructureBodyContent": {
                            "nested": {
                                "normalized_alignment": {
                                    "nested": {
                                        "characters": {
                                            "mode": "edit",
                                            "items": [
                                                null
                                            ]
                                        },
                                        "character_start_times_seconds": {
                                            "mode": "edit",
                                            "items": [
                                                null
                                            ]
                                        },
                                        "character_end_times_seconds": {
                                            "mode": "edit",
                                            "items": [
                                                null
                                            ]
                                        }
                                    }
                                }
                            }
                        },
                        "paginationType": {
                            "label": "Empty"
                        }
                    }
                },
                "parameters": [
                    {
                        "name": "authenticationType",
                        "type": "select",
                        "label": "Authentication type",
                        "required": true,
                        "validate": {
                            "enum": [
                                "noAuth",
                                "apiKey",
                                "basicAuth",
                                "oAuth"
                            ]
                        }
                    },
                    {
                        "name": "tlsType",
                        "type": "select",
                        "label": "Transport layer security (TLS)",
                        "validate": {
                            "enum": [
                                "mTls",
                                "tls"
                            ]
                        }
                    },
                    {
                        "name": "proxyKeychain",
                        "type": "keychain:proxy",
                        "label": "Proxy"
                    }
                ],
                "expect": [
                    {
                        "name": "url",
                        "type": "url",
                        "label": "URL",
                        "required": true
                    },
                    {
                        "name": "method",
                        "type": "select",
                        "label": "Method",
                        "required": true,
                        "validate": {
                            "enum": [
                                "get",
                                "head",
                                "post",
                                "put",
                                "patch",
                                "delete",
                                "options"
                            ]
                        }
                    },
                    {
                        "name": "headers",
                        "type": "array",
                        "label": "Headers",
                        "spec": {
                            "name": "value",
                            "label": "Header",
                            "type": "collection",
                            "spec": [
                                {
                                    "name": "name",
                                    "label": "Name",
                                    "type": "text",
                                    "required": true,
                                    "validate": {
                                        "pattern": "^[-!#$%&'*+.^_`|~0-9A-Za-z]+$"
                                    }
                                },
                                {
                                    "name": "value",
                                    "label": "Value",
                                    "type": "text"
                                }
                            ]
                        }
                    },
                    {
                        "name": "queryParameters",
                        "type": "array",
                        "label": "Query parameters",
                        "spec": {
                            "name": "value",
                            "label": "Parameter",
                            "type": "collection",
                            "spec": [
                                {
                                    "name": "name",
                                    "label": "Name",
                                    "type": "text",
                                    "required": true
                                },
                                {
                                    "name": "value",
                                    "label": "Value",
                                    "type": "text"
                                }
                            ]
                        }
                    },
                    {
                        "name": "contentType",
                        "type": "select",
                        "label": "Body content type",
                        "validate": {
                            "enum": [
                                "json",
                                "multipart",
                                "urlEncoded",
                                "custom"
                            ]
                        }
                    },
                    {
                        "name": "parseResponse",
                        "type": "boolean",
                        "label": "Parse response",
                        "required": true
                    },
                    {
                        "name": "stopOnHttpError",
                        "type": "boolean",
                        "label": "Return error if HTTP request fails",
                        "required": true
                    },
                    {
                        "name": "timeout",
                        "type": "uinteger",
                        "label": "Timeout",
                        "validate": {
                            "min": 1,
                            "max": 300
                        }
                    },
                    {
                        "name": "allowRedirects",
                        "type": "boolean",
                        "label": "Allow redirects",
                        "required": true
                    },
                    {
                        "name": "shareCookies",
                        "type": "boolean",
                        "label": "Share cookies with other HTTP modules",
                        "required": true
                    },
                    {
                        "name": "requestCompressedContent",
                        "type": "boolean",
                        "label": "Request compressed content",
                        "required": true
                    },
                    {
                        "name": "inputMethod",
                        "type": "select",
                        "label": "Body input method",
                        "required": true,
                        "validate": {
                            "enum": [
                                "dataStructure",
                                "jsonString"
                            ]
                        }
                    },
                    {
                        "name": "bodyDataStructure",
                        "type": "udt",
                        "label": "Body structure",
                        "required": true
                    },
                    {
                        "name": "dataStructureBodyContent",
                        "type": "collection",
                        "label": "Body content",
                        "spec": [
                            {
                                "name": "numero_regla",
                                "type": "text",
                                "label": null
                            },
                            {
                                "name": "guion",
                                "type": "text",
                                "label": null
                            },
                            {
                                "name": "subtitles_mode",
                                "type": "text",
                                "label": null
                            },
                            {
                                "name": "audio_base64",
                                "type": "text",
                                "label": null
                            },
                            {
                                "name": "normalized_alignment",
                                "type": "collection",
                                "label": null,
                                "spec": [
                                    {
                                        "name": "characters",
                                        "type": "array",
                                        "label": null,
                                        "spec": {
                                            "type": "text",
                                            "name": "value"
                                        }
                                    },
                                    {
                                        "name": "character_start_times_seconds",
                                        "type": "array",
                                        "label": null,
                                        "spec": {
                                            "type": "text",
                                            "name": "value"
                                        }
                                    },
                                    {
                                        "name": "character_end_times_seconds",
                                        "type": "array",
                                        "label": null,
                                        "spec": {
                                            "type": "text",
                                            "name": "value"
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "name": "paginationType",
                        "type": "select",
                        "label": "Pagination type",
                        "validate": {
                            "enum": [
                                "offsetBased",
                                "pageBased",
                                "urlBased",
                                "tokenBased"
                            ]
                        }
                    }
                ],
                "interface": [
                    {
                        "name": "data",
                        "label": "Data",
                        "type": "any"
                    },
                    {
                        "name": "statusCode",
                        "label": "Status Code",
                        "type": "number"
                    },
                    {
                        "name": "headers",
                        "label": "Headers",
                        "type": "collection",
                        "spec": [
                            {
                                "name": "content-length",
                                "label": "Content-Length",
                                "type": "text"
                            },
                            {
                                "name": "content-encoding",
                                "label": "Content-Encoding",
                                "type": "text"
                            },
                            {
                                "name": "content-type",
                                "label": "Content-Type",
                                "type": "text"
                            },
                            {
                                "name": "server",
                                "label": "Server",
                                "type": "text"
                            },
                            {
                                "name": "cache-control",
                                "label": "Cache-Control",
                                "type": "text"
                            },
                            {
                                "name": "set-cookie",
                                "label": "Set-Cookie",
                                "type": "array",
                                "spec": {
                                    "type": "text"
                                }
                            }
                        ]
                    }
                ]
            }
        },
        {
            "id": 16,
            "module": "google-sheets:updateRow",
            "version": 2,
            "parameters": {
                "__IMTCONN__": 7739710
            },
            "mapper": {
                "mode": "select",
                "valueInputOption": "USER_ENTERED",
                "from": "drive",
                "spreadsheetId": "/1h8RyVWn87dx53-FKhYol6QvpYt51ZFfaWUDFgd3ur0U",
                "sheetId": "Hoja 1",
                "rowNumber": "{{1.`__ROW_NUMBER__`}}",
                "includesHeaders": true,
                "useColumnHeaders": false,
                "values": {
                    "3": "terminado",
                    "5": "audio_{{1.`0`}}.mp3",
                    "6": "https://ffmpeg-render-api-production-1143.up.railway.app{{24.data.video_url}}"
                }
            },
            "metadata": {
                "designer": {
                    "x": 2400,
                    "y": 0
                },
                "restore": {
                    "parameters": {
                        "__IMTCONN__": {
                            "label": "My Google connection (faithinthelion@gmail.com)",
                            "data": {
                                "scoped": "true",
                                "connection": "google"
                            }
                        }
                    },
                    "expect": {
                        "mode": {
                            "label": "Search by path"
                        },
                        "valueInputOption": {
                            "mode": "chose",
                            "label": "User entered"
                        },
                        "from": {
                            "label": "My Drive"
                        },
                        "spreadsheetId": {
                            "path": [
                                "Reglas Invisibles - Estrategia Contenido"
                            ]
                        },
                        "sheetId": {
                            "label": "Hoja 1"
                        },
                        "includesHeaders": {
                            "label": "Yes"
                        },
                        "useColumnHeaders": {
                            "nested": [
                                {
                                    "name": "values",
                                    "spec": [
                                        {
                                            "name": "0",
                                            "type": "text",
                                            "label": "id (A)"
                                        },
                                        {
                                            "name": "1",
                                            "type": "text",
                                            "label": "tema (B)"
                                        },
                                        {
                                            "name": "2",
                                            "type": "text",
                                            "label": "hook (C)"
                                        },
                                        {
                                            "name": "3",
                                            "type": "text",
                                            "label": "estado (D)"
                                        },
                                        {
                                            "name": "4",
                                            "type": "text",
                                            "label": "guion (E)"
                                        },
                                        {
                                            "name": "5",
                                            "type": "text",
                                            "label": "audio_url (F)"
                                        },
                                        {
                                            "name": "6",
                                            "type": "text",
                                            "label": "video_url (G)"
                                        },
                                        {
                                            "name": "7",
                                            "type": "text",
                                            "label": "titulo_youtube (H)"
                                        },
                                        {
                                            "name": "8",
                                            "type": "text",
                                            "label": "desc_youtube (I)"
                                        },
                                        {
                                            "name": "9",
                                            "type": "text",
                                            "label": "desc_tiktok (J)"
                                        },
                                        {
                                            "name": "10",
                                            "type": "text",
                                            "label": "desc_instagram (K)"
                                        },
                                        {
                                            "name": "11",
                                            "type": "text",
                                            "label": "desc_facebook (L)"
                                        },
                                        {
                                            "name": "12",
                                            "type": "text",
                                            "label": "hashtags (M)"
                                        },
                                        {
                                            "name": "13",
                                            "type": "text",
                                            "label": "(N)"
                                        },
                                        {
                                            "name": "14",
                                            "type": "text",
                                            "label": "(O)"
                                        },
                                        {
                                            "name": "15",
                                            "type": "text",
                                            "label": "(P)"
                                        },
                                        {
                                            "name": "16",
                                            "type": "text",
                                            "label": "(Q)"
                                        },
                                        {
                                            "name": "17",
                                            "type": "text",
                                            "label": "(R)"
                                        },
                                        {
                                            "name": "18",
                                            "type": "text",
                                            "label": "(S)"
                                        },
                                        {
                                            "name": "19",
                                            "type": "text",
                                            "label": "(T)"
                                        },
                                        {
                                            "name": "20",
                                            "type": "text",
                                            "label": "(U)"
                                        },
                                        {
                                            "name": "21",
                                            "type": "text",
                                            "label": "(V)"
                                        },
                                        {
                                            "name": "22",
                                            "type": "text",
                                            "label": "(W)"
                                        },
                                        {
                                            "name": "23",
                                            "type": "text",
                                            "label": "(X)"
                                        },
                                        {
                                            "name": "24",
                                            "type": "text",
                                            "label": "(Y)"
                                        },
                                        {
                                            "name": "25",
                                            "type": "text",
                                            "label": "(Z)"
                                        }
                                    ],
                                    "type": "collection",
                                    "label": "Values in columns",
                                    "metadata": [
                                        [
                                            [
                                                "id",
                                                "tema",
                                                "hook",
                                                "estado",
                                                "guion",
                                                "audio_url",
                                                "video_url",
                                                "titulo_youtube",
                                                "desc_youtube",
                                                "desc_tiktok",
                                                "desc_instagram",
                                                "desc_facebook",
                                                "hashtags"
                                            ]
                                        ]
                                    ]
                                }
                            ],
                            "label": "No"
                        }
                    }
                },
                "parameters": [
                    {
                        "name": "__IMTCONN__",
                        "type": "account:google",
                        "label": "Connection",
                        "required": true
                    }
                ],
                "expect": [
                    {
                        "name": "mode",
                        "type": "select",
                        "label": "Search Method",
                        "required": true,
                        "validate": {
                            "enum": [
                                "select",
                                "fromAll",
                                "map"
                            ]
                        }
                    },
                    {
                        "name": "valueInputOption",
                        "type": "select",
                        "label": "Value input option",
                        "validate": {
                            "enum": [
                                "USER_ENTERED",
                                "RAW"
                            ]
                        }
                    },
                    {
                        "name": "from",
                        "type": "select",
                        "label": "Drive",
                        "required": true,
                        "validate": {
                            "enum": [
                                "drive",
                                "share",
                                "team"
                            ]
                        }
                    },
                    {
                        "name": "spreadsheetId",
                        "type": "file",
                        "label": "Spreadsheet Name",
                        "required": true
                    },
                    {
                        "name": "sheetId",
                        "type": "select",
                        "label": "Sheet Name",
                        "required": true
                    },
                    {
                        "name": "rowNumber",
                        "type": "uinteger",
                        "label": "Row number",
                        "required": true
                    },
                    {
                        "name": "includesHeaders",
                        "type": "select",
                        "label": "Table contains headers",
                        "required": true,
                        "validate": {
                            "enum": [
                                true,
                                false
                            ]
                        }
                    },
                    {
                        "name": "useColumnHeaders",
                        "type": "select",
                        "label": "Use column headers as IDs of the columns",
                        "required": true,
                        "validate": {
                            "enum": [
                                true,
                                false
                            ]
                        }
                    },
                    {
                        "name": "values",
                        "type": "collection",
                        "label": "Values in columns",
                        "metadata": [
                            [
                                [
                                    "id",
                                    "tema",
                                    "hook",
                                    "estado",
                                    "guion",
                                    "audio_url",
                                    "video_url",
                                    "titulo_youtube",
                                    "desc_youtube",
                                    "desc_tiktok",
                                    "desc_instagram",
                                    "desc_facebook",
                                    "hashtags"
                                ]
                            ]
                        ],
                        "spec": [
                            {
                                "name": "0",
                                "type": "text",
                                "label": "id (A)"
                            },
                            {
                                "name": "1",
                                "type": "text",
                                "label": "tema (B)"
                            },
                            {
                                "name": "2",
                                "type": "text",
                                "label": "hook (C)"
                            },
                            {
                                "name": "3",
                                "type": "text",
                                "label": "estado (D)"
                            },
                            {
                                "name": "4",
                                "type": "text",
                                "label": "guion (E)"
                            },
                            {
                                "name": "5",
                                "type": "text",
                                "label": "audio_url (F)"
                            },
                            {
                                "name": "6",
                                "type": "text",
                                "label": "video_url (G)"
                            },
                            {
                                "name": "7",
                                "type": "text",
                                "label": "titulo_youtube (H)"
                            },
                            {
                                "name": "8",
                                "type": "text",
                                "label": "desc_youtube (I)"
                            },
                            {
                                "name": "9",
                                "type": "text",
                                "label": "desc_tiktok (J)"
                            },
                            {
                                "name": "10",
                                "type": "text",
                                "label": "desc_instagram (K)"
                            },
                            {
                                "name": "11",
                                "type": "text",
                                "label": "desc_facebook (L)"
                            },
                            {
                                "name": "12",
                                "type": "text",
                                "label": "hashtags (M)"
                            },
                            {
                                "name": "13",
                                "type": "text",
                                "label": "(N)"
                            },
                            {
                                "name": "14",
                                "type": "text",
                                "label": "(O)"
                            },
                            {
                                "name": "15",
                                "type": "text",
                                "label": "(P)"
                            },
                            {
                                "name": "16",
                                "type": "text",
                                "label": "(Q)"
                            },
                            {
                                "name": "17",
                                "type": "text",
                                "label": "(R)"
                            },
                            {
                                "name": "18",
                                "type": "text",
                                "label": "(S)"
                            },
                            {
                                "name": "19",
                                "type": "text",
                                "label": "(T)"
                            },
                            {
                                "name": "20",
                                "type": "text",
                                "label": "(U)"
                            },
                            {
                                "name": "21",
                                "type": "text",
                                "label": "(V)"
                            },
                            {
                                "name": "22",
                                "type": "text",
                                "label": "(W)"
                            },
                            {
                                "name": "23",
                                "type": "text",
                                "label": "(X)"
                            },
                            {
                                "name": "24",
                                "type": "text",
                                "label": "(Y)"
                            },
                            {
                                "name": "25",
                                "type": "text",
                                "label": "(Z)"
                            }
                        ]
                    }
                ]
            }
        }
    ],
    "metadata": {
        "instant": false,
        "version": 1,
        "scenario": {
            "roundtrips": 1,
            "maxErrors": 3,
            "autoCommit": true,
            "autoCommitTriggerLast": true,
            "sequential": false,
            "slots": null,
            "confidential": false,
            "dataloss": false,
            "dlq": false,
            "freshVariables": false
        },
        "designer": {
            "orphans": [
                [
                    {
                        "id": 33,
                        "module": "pcloud:uploadFile",
                        "version": 1,
                        "parameters": {
                            "__IMTCONN__": 7748245
                        },
                        "mapper": {
                            "data": "{{9.data}}",
                            "path": "/My Videos - Reglas Invisibles",
                            "source": "file",
                            "filename": "audio_{{{{1.`0`}}}}.mp3",
                            "overwrite": false
                        },
                        "metadata": {
                            "designer": {
                                "x": 0,
                                "y": 300,
                                "messages": [
                                    {
                                        "category": "link",
                                        "severity": "warning",
                                        "message": "The module is not connected to the data flow."
                                    },
                                    {
                                        "category": "reference",
                                        "severity": "warning",
                                        "message": "Referenced module 'Google Sheets - Search Rows' [1] is not accessible."
                                    },
                                    {
                                        "category": "reference",
                                        "severity": "warning",
                                        "message": "Referenced module 'HTTP - Make a request' [9] is not accessible."
                                    }
                                ]
                            },
                            "restore": {
                                "expect": {
                                    "path": {
                                        "mode": "chose"
                                    },
                                    "source": {
                                        "label": "By File"
                                    },
                                    "overwrite": {
                                        "mode": "chose"
                                    }
                                },
                                "parameters": {
                                    "__IMTCONN__": {
                                        "data": {
                                            "scoped": "true",
                                            "connection": "pcloud"
                                        },
                                        "label": "My pCloud connection (faithinthelion@gmail.com)"
                                    }
                                }
                            },
                            "parameters": [
                                {
                                    "name": "__IMTCONN__",
                                    "type": "account:pcloud",
                                    "label": "Connection",
                                    "required": true
                                }
                            ],
                            "expect": [
                                {
                                    "mode": "edit",
                                    "name": "path",
                                    "type": "folder",
                                    "label": "Target Folder",
                                    "required": true
                                },
                                {
                                    "name": "source",
                                    "type": "select",
                                    "label": "Choose a Source to Upload",
                                    "required": true,
                                    "validate": {
                                        "enum": [
                                            "file",
                                            "url"
                                        ]
                                    }
                                },
                                {
                                    "name": "overwrite",
                                    "type": "boolean",
                                    "label": "Overwrite File",
                                    "required": true
                                },
                                {
                                    "name": "filename",
                                    "type": "filename",
                                    "label": "File Name",
                                    "required": true
                                },
                                {
                                    "name": "data",
                                    "type": "buffer",
                                    "label": "Data",
                                    "required": true
                                }
                            ]
                        }
                    }
                ]
            ]
        },
        "zone": "us2.make.com",
        "notes": []
    }
}
