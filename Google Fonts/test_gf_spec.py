#MenuTitle: Test repo matches gf-checklist structure
# coding: utf-8

'''
Check project fulfills Google Font project Spec.

'''
import os
import re

__author__ = 'Marc Foley'
__version__ = '0.001'

try:
    __glyphsfile__ = Glyphs.font.filepath
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__glyphsfile__), '..'))
except NameError:
    project_dir = os.getcwd()


PROJECT_FILES = {
    'licence': 'OFL.txt',
    'contributors': 'CONTRIBUTORS.txt',
    'trademark': 'TRADEMARKS.txt',
    'readme': 'README.md',
    'gitignore': '.gitignore'
    }

COMPULSORY_FOLDERS = [
    'sources',
    'fonts'
    ]

SETTINGS = {
    'upm': 1000,
    'fstype': [],
}

LICENCE_META = 'This Font Software is licensed under the SIL Open Font License, Version 1.1. This license is available with a FAQ at: http://scripts.sil.org/OFL'
LICENCE_URL_META = 'http://scripts.sil.org/OFL'


def file_exists(proj_file, project_path):
    if proj_file in os.listdir(project_path):
        print('PASS: %s exists' % proj_file)
        return True
    else:
        print('ERROR: %s is missing' % proj_file)
        return False


def folders_exist(directory):
    '''Check project has compulsory folders'''
    folders = []
    for f in os.listdir(directory):
        abs_file_path = os.path.join(directory, f)
        if os.path.isdir(abs_file_path):
            folders.append(f)

    for f in COMPULSORY_FOLDERS:
        if f not in folders:
            print('ERROR: %s folder missing' % f)
        else:
            print('PASS: %s folder exists' % f)


def check_ofl_matches_copyright_string(ofl, c_string):
    if c_string not in ofl.readlines()[0].decode('utf-8'):
        print('ERROR: First line of ofl does not match copyright')
        return False
    else:
        print('PASS: copyright matches')
        return True

def check_copyright_string_contains(c_string, string):
    if string in c_string:
        print('PASS: %s in "%s"' % (string, c_string))
        return True
    else:
        print('ERROR: %s not in "%s"' % (string, c_string))
        return False


def check_vendor_id_string(family_vendor):
    print('***Check vendorID***')
    if family_vendor:
        print 'PASS: font has vendorId\n'
        return True
    else:
        print 'POSSIBLE ERROR: font is missing vendorId\n'
        return False


def check_family_upm(family_upm):
    '''Check upm is 1000'''
    print('***Check font upm***')
    if int(family_upm) != SETTINGS['upm']:
        print 'POSSIBLE ERROR: Family upm is not equal to %s\n' % SETTINGS['upm']
        return False
    else:
        print('PASS: Family upm is equal to %s\n' % SETTINGS['upm'])
        return True


def check_family_name(fontname):
    '''Check if family name has non ascii characters as well as
    dashes, numbers and diacritics as well.'''
    print('***Check family name has only ASCII characters***')
    try:
        fontname.decode('ascii')
        illegal_char_check = re.search(r'[\-\\/0-9]+', fontname)
        if illegal_char_check:
            print('ERROR: Font family "%s", contains numbers, slashes or dashes.' % fontname)
            return False
    except UnicodeDecodeError:
        print('ERROR: Font family name %s, has non ascii characters' % fontname)
        return False
    print('PASS: Family name is correct\n')
    return True


def check_license_string(family_license_string):
    print('***Check License string***')
    if family_license_string == LICENCE_META:
        print('PASS: Family license string is correct\n')
        return True
    else:
        print('ERROR: Family license string is incorrect\n')
        return True


def check_license_url_string(family_license_url):
    print('***Check License URL string***')
    if family_license_url == LICENCE_URL_META:
        print('PASS: Family license url is correct\n')
        return False
    else:
        print('ERROR: Family license url string is incorrect\n')
        return True


def check_family_fstype(font_fstype):
    print('***Check fsType***')
    if font_fstype in (SETTINGS['fstype'], str(SETTINGS['fstype'])):
        print('PASS: Family fsType matches %s\n' % SETTINGS['fstype'])
    else:
        print('ERROR: Family fsType does not match %s\n' % SETTINGS['fstype'])

def main():
    # Check project structure
    font = Glyphs.font
    Glyphs.showMacroWindow()
    file_exists(PROJECT_FILES['readme'], project_dir)
    file_exists(PROJECT_FILES['licence'], project_dir)
    file_exists(PROJECT_FILES['contributors'], project_dir)
    folders_exist(project_dir)

    if file_exists(PROJECT_FILES['licence'], project_dir):
        with open(os.path.join(project_dir, PROJECT_FILES['licence']), 'r') as ofl_file:
            check_ofl_matches_copyright_string(ofl_file, Glyphs.fonts[0].copyright)
            check_copyright_string_contains(Glyphs.fonts[0].copyright, 'Project Authors')
    else:
        print('cannot check first line of OFL matches copyright string')

    if font.customParameters['trademark']:
        if file_exists(PROJECT_FILES['trademark'], project_dir):
            print 'PASS: Font has trademark and file is present'
        else:
            print 'POSSIBLE ERROR: Font has trademark but no %s' % PROJECT_FILES['trademark']

    if file_exists(PROJECT_FILES['trademark'], project_dir):
        if font.customParameters['trademark']:
            print 'PASS: Font has trademark and file is present'
        else:
            print 'POSSIBLE ERROR: %s file exists but font does not have trademark' % PROJECT_FILES['trademark']

    check_vendor_id_string(font.customParameters['vendorID'])

    check_license_string(font.customParameters['license'])
    check_license_url_string(font.customParameters['licenseURL'])

    check_family_name(font.familyName)
    check_family_upm(font.upm)
    check_family_fstype(font.customParameters['fsType'])


if __name__ == '__main__':
    main()
