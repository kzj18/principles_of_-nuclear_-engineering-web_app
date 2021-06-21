from pandas import DataFrame

DRAW_LIST = {
    "235U": 0.1,
    "236U": 1,
    "239Pu": 1,
    "240Pu": 1,
    "241Pu": 1,
    "242Pu": 1
}

SETTINGS = {
    "t": 365,
    "Method": "Power",
    "Flux": 1e14,
    "Power": 3e2,
    "Weight": 1,
    "DT": 10,
    "Accuracy": 1e-3,
    "Initial": {
        "234U": 1,
        "235U": 19,
        "236U": 0,
        "238U": 980,
        "239U": 0,
        "239Np": 0,
        "239Pu": 0,
        "240Pu": 0,
        "241Pu": 0,
        "242Pu": 0,
        "241Am": 0
    }
}

DATA = DataFrame(
    data=[
        [24,    '234U',     0,  'Original',             'Neutron Absorbtion',                   0,      100,    None,       '235U燃耗链'],
        [25,    '235U',     24, 'Neutron Absorbtion',   'Neutron Absorbtion',                   585,    99,     None,       '235U燃耗链'],
        [26,    '236U',     25, 'Neutron Absorbtion',   'Neutron Absorbtion',                   0,      5.1,    None,       '235U燃耗链'],
        [28,    '238U',     0,  'Original',             'Neutron Absorbtion',                   0,      2.7,    None,       '238U燃耗链'],
        [29,    '239U',     28, 'Neutron Absorbtion',   'Neutron Absorbtion and Beta Decay',    15,     22,     4.93E-04,   '238U燃耗链'],
        [39,    '239Np',    29, 'Beta Decay',           'Neutron Absorbtion and Beta Decay',    0,      60,     3.41E-06,   '238U燃耗链'],
        [49,    '239Pu',    39, 'Beta Decay',           'Neutron Absorbtion',                   750,    271,    None,       '238U燃耗链'],
        [40,    '240Pu',    49, 'Neutron Absorbtion',   'Neutron Absorbtion',                   0,      290,    None,       '238U燃耗链'],
        [41,    '241Pu',    40, 'Neutron Absorbtion',   'Neutron Absorbtion and Beta Decay',    1010,   361,    1.53E-09,   '238U燃耗链'],
        [42,    '242Pu',    41, 'Neutron Absorbtion',   'Neutron Absorbtion',                   0,      19,     None,       '238U燃耗链'],
        [51,    '241Am',    41, 'Beta Decay',           'Neutron Absorbtion',                   3,      600,    None,       '238U燃耗链'],
    ],
    columns=['序号', '核素名称', '父级核素序号', '父级转换类型', '子级转换类型', '裂变截面（Barns）', '捕获截面（Barns）', '衰减常数（s^-1）', '备注']
)