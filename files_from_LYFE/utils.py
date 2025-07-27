import os
import datetime as dt

import configparser

import numpy as np
import os
import re  # regular expressions

_UNSET = object()  # A good practice for dynamically creating default values

# function to set the filename based on the current folder
def set_filename(filename, folder="outputs"):
    """
    This function sets the filename based on the current folder to avoid hard-coding filanames.
    
    Parameters
    ----------
    filename : str
        The filename of the output file.
    folder : str, optional
        The folder where the file should be located. The default is "outputs".
        
    Returns
    -------
    str
        The complete filename including the path.
    """
    
    lyfe_config, airlyfe_config = read_config()
    
    input_path = lyfe_config.get('General', 'input_path')
    output_path = lyfe_config.get('General', 'output_path')
    
    if folder == "inputs":
        return os.path.join(input_path, filename)
    elif folder == "outputs":
        return os.path.join(output_path, filename)
    else:
        raise Exception("The folder " + folder + " is not supported. Currently supported: outputs, inputs.")
    
    ### old code that worked without the ExtendedConfigParser below
    
    # check whether the current file is in the correct folder to read in everything correctly
    current_path = os.path.dirname(os.path.realpath(__file__))
    
    if current_path.endswith("submodules"):
        # get the path where airfyle is located
        dir_path = os.path.dirname(os.path.dirname(current_path)) 
    elif current_path.endswith("lca_uncertainties"):
        dir_path = os.path.dirname(current_path)
    else:
        raise Exception("Your file is not in the folder ...\\airlyfe\\airlyfe\\submodules or ...\\airlyfe\\lca_uncertainties, please move it there.\n \
            The current path is: " + current_path)

    # add the filename to the path
    if folder == "outputs":       
        filename_complete = os.path.join(dir_path, 'projects\\workstation_project_mc\\outputs', filename)
    elif folder == "inputs":
        filename_complete = os.path.join(dir_path, 'projects\\workstation_project_mc\\inputs', filename)
    else:
        raise Exception("The folder " + folder + " is not supported. Currently supported: outputs, inputs.")
    
    return filename_complete

def tprint(args):
    """
    Print a statement with the current time into the console.

    The format is: ``HH:MM:SS | printstatement``, e.g.
    ``13:46:02 | Airlyfe started``.

    Parameters
    ----------
    args : Print statement passed to print()

    Returns
    -------
    None
    """

    stamp = str(dt.datetime.now().strftime('%H:%M:%S'))
    print(stamp + ' | ' + args)
    
def read_config():
    """
    Read the lyfe_config.ini and referencecase.ini and return both ConfigParserObjects.

    Returns
    -------
    lyfe_config : ExtendedConfigParser
        Configuration based on lyfe_config.ini with sections, keys and options
    airlyfe_config : ExtendedConfigParser
        Configuration based on the referencecase.ini with sections, keys and options
    """

    # Determine and save paths of current file/folder
    dpath_lyfe = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))
    fpath_lyfe_cfg = os.path.realpath(
        os.path.join(dpath_lyfe, 'lyfe_config.ini')
    )

    # Read LYFE configuration file (in the same folder as lyfe.py)
    lyfe_config = ExtendedConfigParser(inline_comment_prefixes='#')
    lyfe_config.read_ini(fpath_lyfe_cfg)

    # Now determine the project path and save them
    dpath_project = os.path.realpath(os.path.join(
        dpath_lyfe, 'projects', lyfe_config.get('General', 'projectName')
    ))
    dpath_inputs = os.path.realpath(os.path.join(dpath_project, 'inputs'))
    dpath_outputs = os.path.realpath(os.path.join(dpath_project, 'outputs'))

    # Write these paths to the config file itself
    lyfe_config.set('General', 'abs_path_lyfe', dpath_lyfe)
    lyfe_config.set('General', 'project_path', dpath_project)
    lyfe_config.set('General', 'input_path', dpath_inputs)
    lyfe_config.set('General', 'output_path', dpath_outputs)
    
    # Determine the reference config file. It has a special meaning: If the
    # User provides additional .ini files, they can be written "relative"
    # to the reference. In short: Only those parameters have to be listed,
    # which differ between the reference and study case.
    fpath_refcase_cfg = os.path.join(
        lyfe_config.getpath('General', 'input_path'),
        lyfe_config.get('General', 'reference_config_name')
    )
    lyfe_config.set('General', 'fpath_to_reference_cfg', fpath_refcase_cfg)
    
    # read the referencecase.ini file
    airlyfe_config = ExtendedConfigParser(inline_comment_prefixes='#')
    airlyfe_config.read_ini(lyfe_config.getpath('General', 'fpath_to_reference_cfg'))

    return lyfe_config, airlyfe_config

# copied and slightly shortened class definition from airlyfe/preprocessing/config_parser.py
class ExtendedConfigParser(configparser.ConfigParser):
    """
    Powerful extension of the regular ConfigParser.

    Most inputs of LYFE are configuration files in the .ini format. To read
    those, a ConfigParser is needed. To intelligently read those, this class
    is provided. It contains extra functions such as reading lists, converting
    read inputs to certain types (e.g. timedeltas, floats, ints, ...). Most of
    this class can be used anywhere. Only very few features are specific to
    AirLYFE.

    Methods
    -------
    read_ini
        Read ``*.ini`` file while tolerating the encoding format.
    duplicate
        Duplicate current ExtendedConfigParser object.
    getstr
        Read entry and convert to string. Has better exception function.
    getlist
        Read entry that holds a comma-separated list with string entries.
    setlist
        Write entry that holds a comma-separated list with string entries.
    getlistint
        Read entry that holds a comma-separated list with int entries.
    getlistfloat
        Read entry that holds a comma-separated list with float entries.
    getlisttime
        Read entry that holds a time in the HH:MM or HH:MM:SS format.
    getlistdur
        Read entry that holds a comma-separated list with timedelta entries
        in a format-tolerant way.
    str2dur
        Convert string to datetime.timedelta. Internally used function.
    getpath
        Return os.path.normpath() of a saved path.
    getdatetime
        Read entry that holds a datetime entry.
    printtoconsole
        Print the current config information into the console.

    See Also
    --------
    configparser.ConfigParser
        Parent Class
    """

    def read_ini(self, params):
        """
        Read ``*.ini`` file while tolerating the encoding format.

        Users sometimes open the ``*.ini`` file in an editor that automatically
        saves it using a non UTF-8 format (e.g. UTF-8-BOM or ANSI). This
        intermediate function incorporates a tolerant file reading by trying to
        read it, and if it fails due to a certain error, open and rewrite it as
        UTF-8. Tested on UTF-8-BOM and ANSI.

        Parameters
        ----------
        params : str
            Whatever you would pass to the ConfigParser.read() method.

        Returns
        -------
        None
        """

        try:
            self.read(params)
        except configparser.MissingSectionHeaderError:
            if isinstance(params, list):
                for param in params:
                    bom_file = param
                    s = open(bom_file, mode='r', encoding='utf-8-sig').read()
                    open(bom_file, mode='w', encoding='utf-8').write(s)
            else:
                bom_file = params
                s = open(bom_file, mode='r', encoding='utf-8-sig').read()
                open(bom_file, mode='w', encoding='utf-8').write(s)
            self.read(params)

    def duplicate(self):
        """
        Duplicate current ExtendedConfigParser object.

        Needed for certain multiprocessing actions.

        Returns
        -------
        ExtendedConfigParser
            Duplicated object,
        """

        duplicate = ExtendedConfigParser()
        for section in self.sections():
            if not duplicate.has_section(section):
                duplicate.add_section(section)

            for option in self.options(section):
                duplicate.set(section, option, self.get(section, option))

        return duplicate

    def getstr(self, section, option, fallback=_UNSET):
        """
        Read entry and convert to string. Has better exception function.

        The normal fallback implementation is silent. This function tells the
        user if the fallback method has been used.

        Parameters
        ----------
        section : str
            Section in .ini file defined by brackets, e.g. [Operation].
        option : str
            Parameter in section which gets a value, e.g. option = value.
        fallback : str, optional
            If either the section or the option within the section is not
            found, this is used.

        Returns
        -------
        str
        """

        strresult = super().get(section, option, fallback=fallback)
        if fallback is strresult and fallback is not _UNSET:
            print("Warning: I could not find a value in [%s]->%s, "
                  "using the provided fallback: %s"
                  % (section, option, fallback))
        elif fallback is strresult and fallback is _UNSET:
            raise Exception("Couldn't find it")
        return strresult

    def getlist(self, section, option, fallback=_UNSET, nested=False):
        """
        Read entry that holds a comma-separated list with string entries.

        Parameters
        ----------
        section : str
            Section in .ini file defined by brackets, e.g. [Operation].
        option : str
            Parameter in section which gets a value, e.g. option = value.
        fallback : str, optional
            If either the section or the option within the section is not
            found, this is used.
        nested : boolean, default False
            If true, the parser expects the value of the option to be a nested
            list, i.e. a list within a list. This is primarily used for the
            maintenance section.

        Returns
        -------
        list
            A list with entries of the string type, e.g. ['1', 'two'] for a
            non-nested list or [['1', 'two'], ['three', '4.0']] for a nested
            list.
        """

        try:
            value = self.get(section, option)
        except (configparser.NoSectionError, configparser.NoOptionError):
            if fallback is _UNSET:
                raise
            else:
                return fallback

        if not nested:
            return list(filter(None, (x.strip() for x in value.split(','))))
        else:
            valuelist = re.findall("\[([^[\]]*)\]", value)
            return [x.split(', ') for x in valuelist]

    def setlist(self, section, option, value, mode='create'):
        """
        Write entry that holds a comma-separated list with string entries.

        Parameters
        ----------
        section : str
            Section in .ini file defined by brackets, e.g. [Operation].
        option : str
            Parameter in section which gets a value, e.g. option = value.
        value : list
            A list with entries of the string type, e.g. ['1', 'two'].
        mode : str, {'create', 'extend'}
            Whether to create a new list or extend an existing one.

        Returns
        -------
        None
        """

        # convert each element in the list to a string
        # e.g. ['3.2', '4.2', '2.0'] when it was [3.2, 4.2, 2.0]
        stringlist = [str(el) for el in value]

        # join the elements to one overall string
        stringvalue = (', ').join(stringlist)  # e.g. '3.2, 4.2, 2.0'

        # if the input value of this code contains a stringlist with more than
        # one item in this list, it will be appended to the existing list or
        # the new list as it is the problem is, if the items in the stringlist
        # are divided with a comma in section Maintenance (option = Included in),
        # the resulting list can't differentiate between the individual items
        # of this specisfic stringlist, so it needs to be adjusted.
        # EXAMPLE: if the maintenance excel file is read and the values within
        # the option included_in per check looks like this: 'Daily Check, A'
        # the resulting final list will look like this:
        # 'XX, YY, Daily Check, A, ...' - it is not clear anymore, that the
        # 'Daily Check, A' belong to one maintenance check and not two.
        # Therefor we need to replace all occurrences of the comma in
        # the stringvalue with a semicolon if the len of value is exactly one:
        if len(value) == 1:
            stringvalue = stringvalue.replace(",", ";")

        if mode == 'create':
            # set the attribute
            self.set(section, option, stringvalue)

        elif mode == 'extend':
            # extend if one exists, create if none exists

            if self.has_option(section, option):
                # Option exists

                # Read the original entry first
                option_to_extend = self.get(section, option)

                # Combine old with new, separated by a comma
                value = (', ').join([option_to_extend, stringvalue])

                self.set(section, option, value)

            else:

                # If the option exists, just set the value
                self.set(section, option, stringvalue)


            """ deactivated since issue #167
            # if the extension is going to be applied, the convention is that
            # braces ([) surround each element
            stringvalue = '[' + stringvalue + ']'  # e.g. '[3.2, 4.2, 2.0]'
            if self.has_option(section, option):  # items already exist
                # read the entry first
                stringtobeextended = self.get(section, option)
                # e.g. '[one, two, three]'

                value = (', ').join([stringtobeextended, stringvalue])
                # e.g. '[one, two, three], [3.2, 4.2, 2.0]'

                self.set(section, option, value)  # set it
            else:  # nothing exists yet
                # create
                self.set(section, option, stringvalue)
            """

    def getlistint(self, section, option, fallback=_UNSET, nested=False):
        """
        Read entry that holds a comma-separated list with int entries.

        Same as getlist(section, option, fallback, nested) but converts the
        list elements to integers.

        Parameters
        ----------
        section : str
            Section in .ini file defined by brackets, e.g. [Operation].
        option : str
            Parameter in section which gets a value, e.g. option = value.
        fallback : str, optional
            If either the section or the option within the section is not
            found, this is used.
        nested : boolean, default False
            If true, the parser expects the value of the option to be a nested
            list, i.e. a list within a list. This is primarily used for the
            maintenance section.

        Returns
        -------
        list
            A list with entries of the integer type, e.g. [1, 2] for a
            non-nested list or [[1, 2], [3, 4]] for a nested list
        """

        valuelist = self.getlist(
            section, option, fallback=fallback, nested=nested)
        if not nested:
            return [int(float(x)) if not np.isnan(float(x))
                    else float(x) for x in valuelist]
        else:
            return [[int(float(x)) if not np.isnan(float(x))
                     else float(x) for x in sublist] for sublist in valuelist]

    def getlistfloat(self, section, option, fallback=_UNSET, nested=False):
        """
        Read entry that holds a comma-separated list with float entries.

        Same as getlist(section, option, fallback, nested) but converts the
        list elements to floats.

        Parameters
        ----------
        section : str
            Section in .ini file defined by brackets, e.g. [Operation].
        option : str
            Parameter in section which gets a value, e.g. option = value.
        fallback : str, optional
            If either the section or the option within the section is not
            found, this is used.
        nested : boolean, default False
            If true, the parser expects the value of the option to be a nested
            list, i.e. a list within a list. This is primarily used for the
            maintenance section.

        Returns
        -------
        list
            A list with entries of the float type, e.g. [1.0, 2.0] for a
            non-nested list or [[1.0, 2.0], [3.0, 4.0]] for a nested list
        """

        valuelist = self.getlist(section, option, fallback=fallback, nested=nested)
        if not nested:
            return [float(x) if x is not None else x for x in valuelist]
        else:
            return [[float(x) if x is not None else x for x in sublist] for sublist in valuelist]

    def getlisttime(self, section, option, nested=False):
        """
        Read entry that holds a time in the HH:MM or HH:MM:SS format.

        In contrast to ``getlisttimedelta``, ``getlisttime`` interprets the
        HH:MM entry to be a time, not a timedelta.

        Parameters
        ----------
        section : str
            Section in .ini file defined by brackets, e.g. [Operation].
        option : str
            Parameter in section which gets a value, e.g. option = value.
        fallback : str, optional
            If either the section or the option within the section is not
            found, this is used.

        Returns
        -------
        datetime.datetime
            The read time object.
        """
        try:
            return [dt.datetime.strptime(x, '%H:%M').time() for x
                    in self.getlist(section, option, nested)]
        except ValueError:
            # time_list = [x for x in self.getlist(section, option, nested)
            #              if np.isnan(x)]
            return [dt.datetime.strptime(x, '%H:%M:%S').time() for x
                    in self.getlist(section, option, nested) if np.isnan(x)]

    def getlistdur(self, section, option, strformat=_UNSET, nested=False):
        """
        Read entry that holds a comma-separated list with timedelta entries
        in a format-tolerant way.

        Parameters
        ----------
        section : str
            Section in .ini file defined by brackets, e.g. [Operation].
        option : str
            Parameter in section which gets a value, e.g. option = value.
        strformat : str
            string format which is used to identify the hours and minuts.
        nested : boolean, default False
            If true, the parser expects the value of the option to be a nested
            list, i.e. a list within a list. This is primarily used for the
            maintenance section.

        Returns
        -------
        list
            A list with entries of the datetime.timedelta entries.
        """

        inputstrlist = self.getlist(section, option, nested=nested)
        if strformat is _UNSET:
            strformatlist = [':', 'hours', 'notfounderror']
        else:
            strformatlist = [strformat, 'notfounderror']

        for strformat in strformatlist:
            try:
                if not nested:
                    durlist = [self.str2dur(el, strformat) for el in inputstrlist]
                else:
                    durlist = []
                    for sublist in inputstrlist:
                        subdurlist = [self.str2dur(el, strformat) for el in sublist]
                        durlist.append(subdurlist)
                break
            except:
                continue

        if strformat == 'notfounderror':
            raise Exception('Specified string format not supported')
        else:
            return durlist

    def str2dur(self, inputstr, strformat):
        """
        Convert string to datetime.timedelta. Internally used function.

        Parameters
        ----------
        inputstr : str
            input string.
        strformat : str
            string format which is used to identify the hours and minuts.

        Returns
        -------
        datetime.timedelta
        """

        if strformat == ':':
            rawsplit = inputstr.split(':')
            dur = dt.timedelta(hours=float(rawsplit[0]), minutes=float(rawsplit[1]))
        else:
            dicttounpack = {strformat: float(inputstr)}
            dur = dt.timedelta(**dicttounpack)
        return dur

    def getpath(self, section, option, fallback=_UNSET):
        """
        Return os.path.normpath() of a saved path.

        Parameters
        ----------
        section : str
            Section in .ini file defined by brackets, e.g. [Operation].
        option : str
            Parameter in section which gets a value, e.g. option = value.
        fallback : str, optional
            If either the section or the option within the section is not
            found, this is used.

        Returns
        -------
        str
            output from os.path.normpath
        """
        stringpath = self.get(section, option, fallback=fallback)
        return os.path.normpath(stringpath)

    def getdatetime(self, section, option, fallback=_UNSET):
        """
        Read entry that holds a datetime entry.

        Formats can be YYYY-MM-DD HH:MM:SS, YYYY-MM-DD HH:MM, or YYYY-MM-DD.

        Parameters
        ----------
        section : str
            Section in .ini file defined by brackets, e.g. [Operation].
        option : str
            Parameter in section which gets a value, e.g. option = value.
        fallback : str, optional
            If either the section or the option within the section is not
            found, this is used.

        Returns
        -------
        datetime.datetime
        """

        value = self.get(section, option, fallback=fallback)
        try:
            return dt.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            pass
        try:
            return dt.datetime.strptime(value, '%Y-%m-%d %H:%M')
        except ValueError:
            pass
        try:
            return dt.datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            raise ValueError(
                'The following config value: \n[%s]\n%s = %s \n'
                'does not match any of the possible formats: '
                '<%%Y-%%m-%%d %%H:%%M:%%S>, <%%Y-%%m-%%d %%H:%%M>, '
                '<%%Y-%%m-%%d>'
                % (section, option, value))

    def print_to_console(self, section=None):
        """
        Print the current config information into the console.

        Parameters
        ----------
        section : str, optional
            You can limit the console printing to one specific section.

        Returns
        -------
        None
        """

        if section is None:
            for section in self.sections():
                print('\n[%s]' % section)
                for key in self[section].keys():
                    print('%s = %s' % (key, self.get(section, key)))
        else:
            print('\n[%s]' % section)
            for key in self[section].keys():
                print('%s = %s' % (key, self.get(section, key)))

def lcia_method_transl(lcia_method_name, category):
    # The translation dictionaries are defined in lca_databases.py.
    lcia_transl_dict = get_lcia_transl_dict(lcia_method_name)

    # Iterate through the translation dictionary to find a match for the given category.
    for key, value in lcia_transl_dict.items():
        # Check if the lowercase version of the category is present in the lowercase version of the
        # dictionary key.
        if category.lower() in key.lower():
            # Return the translated values associated with the matched key.
            return value
            
def get_lcia_transl_dict(lcia_method):
    # The translation dictionaries are needed for the output of the LCA results. If there is no dictionary for the chosen
    # LCIA method, an error occurs.

    # Environmental Footprint (EF v3.0):
    if lcia_method == "'EF v3.0'":

        lcia_transl_dict = {
            'acidification [mol H+-Eq]':
                ('Acidification',
                 'accumulated exceedance (ae)',
                 '[mol H+-Eq]',
                 'ADP'),
            'climate change [kg CO2-Eq]':
                ('Climate Change',
                 'global warming potential (GWP100)',
                 '[kg CO2-Eq]',
                 'CC'),
            'ecotoxicity: freshwater [CTUe]':
                ('Ecotoxicity: Freshwater',
                 'comparative toxic unit for ecosystems (CTUe)',
                 '[CTUe]',
                 'FETP'),
            'energy resources: non-renewable [MJ, net calorific value]':
                ('Energy Resources: Non-Renewable',
                 'abiotic depletion potential (ADP)',
                 '[MJ]',
                 'ECF'),
            'eutrophication: freshwater [kg P-Eq]':
                ('Eutrophication: Freshwater',
                 'fraction of nutrients reaching freshwater end compartment (P)',
                 '[kg P-Eq]',
                 'FEP'),
            'eutrophication: marine [kg N-Eq]':
                ('Eutrophication: Marine',
                 'fraction of nutrients reaching marine end compartment (N)',
                 '[kg N-Eq]',
                 'MEP'),
            'eutrophication: terrestrial [mol N-Eq]':
                ('Eutrophication: Terrestrial',
                 'accumulated exceedance (AE)',
                 '[mol N-Eq]',
                 'TEP'),
            'human toxicity: carcinogenic [CTUh]':
                ('Human Toxicity: Carcinogenic',
                 'comparative toxic unit for human (CTUh)',
                 '[CTUh]',
                 'HHC'),
            'human toxicity: non-carcinogenic [CTUh]':
                ('Human Toxicity: Non-Carcinogenic',
                 'comparative toxic unit for human (CTUh)',
                 '[CTUh]',
                 'HHNC'),
            'ionising radiation: human health [kBq U235-Eq]':
                ('Ionising Radiation',
                 'human exposure efficiency relative to u235',
                 '[kBq U235-Eq]',
                 'IR'),
            'land use [dimensionless]':
                ('Land Use',
                 'soil quality index',
                 '[dimensionless]',
                 'LU'),
            'material resources: metals/minerals [kg Sb-Eq]':
                ('Material Resources: Metals/Minerals',
                 'abiotic depletion potential (ADP)',
                 '[kg Sb-Eq]',
                 'MM'),
            'ozone depletion [kg CFC-11-Eq]':
                ('Ozone Depletion',
                 'ozone depletion potential (ODP)',
                 '[kg CFC-11-Eq]',
                 'ODP'),
            'particulate matter formation [disease incidence]':
                ('Particulate Matter Formation',
                 'impact on human health',
                 '[disease incidence]',
                 'PM'),
            'photochemical oxidant formation: human health [kg NMVOC-Eq]':
                ('Photochemical Oxidant Formation',
                 'tropospheric ozone concentration increase',
                 '[kg NMVOC-Eq]',
                 'POxF'),
            'photochemical ozone formation: human health [kg NMVOC-Eq]':
                ('Photochemical Ozone Formation',
                 'tropospheric ozone concentration increase',
                 '[kg NMVOC-Eq]',
                 'POzF'),
            'water use [m3 world eq. deprived]':
                ('Water Use',
                 'user deprivation potential (deprivation-weighted water consumption)',
                 '[m3 world eq. deprived]',
                 'WS')
        }

    # Environmental Footprint (EF v3.0 no LT):
    elif lcia_method == "'EF v3.0 no LT'":

        lcia_transl_dict = {
            'acidification no LT [mol H+-Eq]':
                ('Acidification',
                 'accumulated exceedance (ae) no LT',
                 '[mol H+-Eq]',
                 'ADP'),
            'climate change no LT [kg CO2-Eq]':
                ('Climate Change',
                 'global warming potential (GWP100) no LT',
                 '[kg CO2-Eq]',
                 'CC'),
            'ecotoxicity: freshwater no LT [CTUe]':
                ('Ecotoxicity: Freshwater',
                 'comparative toxic unit for ecosystems (CTUe) no LT',
                 '[CTUe]',
                 'FETP'),
            'energy resources: non-renewable no LT [MJ, net calorific value]':
                ('Energy Resources: Non-Renewable',
                 'abiotic depletion potential (ADP) no LT',
                 '[MJ]',
                 'ECF'),
            'eutrophication: freshwater no LT [kg P-Eq]':
                ('Eutrophication: Freshwater',
                 'fraction of nutrients reaching freshwater end compartment (P) no LT',
                 '[kg P-Eq]',
                 'FEP'),
            'eutrophication: marine no LT [kg N-Eq]':
                ('Eutrophication: Marine',
                 'fraction of nutrients reaching marine end compartment (N) no LT',
                 '[kg N-Eq]',
                 'MEP'),
            'eutrophication: terrestrial no LT [mol N-Eq]':
                ('Eutrophication: Terrestrial',
                 'accumulated exceedance (AE) no LT',
                 '[mol N-Eq]',
                 'TEP'),
            'human toxicity: carcinogenic no LT [CTUh]':
                ('Human Toxicity: Carcinogenic',
                 'comparative toxic unit for human (CTUh) no LT',
                 '[CTUh]',
                 'HHC'),
            'human toxicity: non-carcinogenic no LT [CTUh]':
                ('Human Toxicity: Non-Carcinogenic',
                 'comparative toxic unit for human (CTUh) no LT',
                 '[CTUh]',
                 'HHNC'),
            'ionising radiation: human health no LT [kBq U235-Eq]':
                ('Ionising Radiation',
                 'human exposure efficiency relative to u235 no LT',
                 '[kBq U235-Eq]',
                 'IR'),
            'land use no LT [dimensionless]':
                ('Land Use',
                 'soil quality index no LT',
                 '[dimensionless]',
                 'LU'),
            'material resources: metals/minerals no LT [kg Sb-Eq]':
                ('Material Resources: Metals/Minerals',
                 'abiotic depletion potential (ADP) no LT',
                 '[kg Sb-Eq]',
                 'MM'),
            'ozone depletion no LT [kg CFC-11-Eq]':
                ('Ozone Depletion',
                 'ozone depletion potential (ODP) no LT',
                 '[kg CFC-11-Eq]',
                 'ODP'),
            'particulate matter formation no LT [disease incidence]':
                ('Particulate Matter Formation',
                 'impact on human health no LT',
                 '[disease incidence]',
                 'PM'),
            'photochemical oxidant formation: human health no LT [kg NMVOC-Eq]':
                ('Photochemical Oxidant Formation',
                 'tropospheric ozone concentration increase no LT',
                 '[kg NMVOC-Eq]',
                 'POxF'),
            'photochemical ozone formation: human health no LT [kg NMVOC-Eq]':
                ('Photochemical Ozone Formation',
                 'tropospheric ozone concentration increase no LT',
                 '[kg NMVOC-Eq]',
                 'POzF'),
            'water use no LT [m3 world eq. deprived]':
                ('Water Use',
                 'user deprivation potential (deprivation-weighted water consumption) no LT',
                 '[m3 world eq. deprived]',
                 'WS')
        }

    # Environmental Footprint (EF v3.1):
    elif lcia_method == "'EF v3.1'":

        lcia_transl_dict = {
            'acidification [mol H+-Eq]':
                ('Acidification',
                 'accumulated exceedance (ae)',
                 '[mol H+-Eq]',
                 'ADP'),
            'climate change [kg CO2-Eq]':
                ('Climate Change',
                 'global warming potential (GWP100)',
                 '[kg CO2-Eq]',
                 'CC'),
            'ecotoxicity: freshwater [CTUe]':
                ('Ecotoxicity: Freshwater',
                 'comparative toxic unit for ecosystems (CTUe)',
                 '[CTUe]',
                 'FETP'),
            'energy resources: non-renewable [MJ, net calorific value]':
                ('Energy Resources: Non-Renewable',
                 'abiotic depletion potential (ADP)',
                 '[MJ]',
                 'ECF'),
            'eutrophication: freshwater [kg P-Eq]': (
                'Eutrophication: Freshwater', 'fraction of nutrients reaching freshwater end compartment (P)',
                '[kg P-Eq]',
                'FEP'),
            'eutrophication: marine [kg N-Eq]':
                ('Eutrophication: Marine',
                 'fraction of nutrients reaching marine end compartment (N)',
                 '[kg N-Eq]',
                 'MEP'),
            'eutrophication: terrestrial [mol N-Eq]':
                ('Eutrophication: Terrestrial',
                 'accumulated exceedance (AE)',
                 '[mol N-Eq]',
                 'TEP'),
            'human toxicity: carcinogenic [CTUh]':
                ('Human Toxicity: Carcinogenic',
                 'comparative toxic unit for human (CTUh)',
                 '[CTUh]',
                 'HHC'),
            'human toxicity: non-carcinogenic [CTUh]':
                ('Human Toxicity: Non-Carcinogenic',
                 'comparative toxic unit for human (CTUh)',
                 '[CTUh]',
                 'HHNC'),
            'ionising radiation: human health [kBq U235-Eq]':
                ('Ionising Radiation',
                 'human exposure efficiency relative to u235',
                 '[kBq U235-Eq]',
                 'IR'),
            'land use [dimensionless]':
                ('Land Use',
                 'soil quality index',
                 '[dimensionless]',
                 'LU'),
            'material resources: metals/minerals [kg Sb-Eq]':
                ('Material Resources: Metals/Minerals',
                 'abiotic depletion potential (ADP)',
                 '[kg Sb-Eq]',
                 'MM'),
            'ozone depletion [kg CFC-11-Eq]':
                ('Ozone Depletion',
                 'ozone depletion potential (ODP)',
                 '[kg CFC-11-Eq]',
                 'ODP'),
            'particulate matter formation [disease incidence]':
                ('Particulate Matter Formation',
                 'impact on human health',
                 '[disease incidence]',
                 'PM'),
            'photochemical oxidant formation: human health [kg NMVOC-Eq]':
                ('Photochemical Oxidant Formation',
                 'tropospheric oxidant concentration increase',
                 '[kg NMVOC-Eq]',
                 'POF'),
            'water use [m3 world eq. deprived]':
                ('Water Use',
                 'user deprivation potential (deprivation-weighted water consumption)',
                 '[m3 world eq. deprived]',
                 'WS')
        }

    # Environmental Footprint (EF v3.1 no LT):
    elif lcia_method == "'EF v3.1 no LT'":

        lcia_transl_dict = {
            'acidification no LT [mol H+-Eq]':
                ('Acidification',
                 'accumulated exceedance (ae) no LT',
                 '[mol H+-Eq]',
                 'ADP'),
            'climate change no LT [kg CO2-Eq]':
                ('Climate Change',
                 'global warming potential (GWP100) no LT',
                 '[kg CO2-Eq]',
                 'CC'),
            'ecotoxicity: freshwater no LT [CTUe]':
                ('Ecotoxicity: Freshwater',
                 'comparative toxic unit for ecosystems (CTUe) no LT',
                 '[CTUe]',
                 'FETP'),
            'energy resources: non-renewable no LT [MJ, net calorific value]':
                ('Energy Resources: Non-Renewable',
                 'abiotic depletion potential (ADP) no LT',
                 '[MJ]',
                 'ECF'),
            'eutrophication: freshwater no LT [kg P-Eq]': (
                'Eutrophication: Freshwater', 'fraction of nutrients reaching freshwater end compartment (P) no LT',
                '[kg P-Eq]',
                'FEP'),
            'eutrophication: marine no LT [kg N-Eq]':
                ('Eutrophication: Marine',
                 'fraction of nutrients reaching marine end compartment (N) no LT',
                 '[kg N-Eq]',
                 'MEP'),
            'eutrophication: terrestrial no LT [mol N-Eq]':
                ('Eutrophication: Terrestrial',
                 'accumulated exceedance (AE) no LT',
                 '[mol N-Eq]',
                 'TEP'),
            'human toxicity: carcinogenic no LT [CTUh]':
                ('Human Toxicity: Carcinogenic',
                 'comparative toxic unit for human (CTUh) no LT',
                 '[CTUh]',
                 'HHC'),
            'human toxicity: non-carcinogenic no LT [CTUh]':
                ('Human Toxicity: Non-Carcinogenic',
                 'comparative toxic unit for human (CTUh) no LT',
                 '[CTUh]',
                 'HHNC'),
            'ionising radiation: human health no LT [kBq U235-Eq]':
                ('Ionising Radiation',
                 'human exposure efficiency relative to u235 no LT',
                 '[kBq U235-Eq]',
                 'IR'),
            'land use no LT [dimensionless]':
                ('Land Use',
                 'soil quality index no LT',
                 '[dimensionless]',
                 'LU'),
            'material resources: metals/minerals no LT [kg Sb-Eq]':
                ('Material Resources: Metals/Minerals',
                 'abiotic depletion potential (ADP) no LT',
                 '[kg Sb-Eq]',
                 'MM'),
            'ozone depletion no LT [kg CFC-11-Eq]':
                ('Ozone Depletion',
                 'ozone depletion potential (ODP) no lT',
                 '[kg CFC-11-Eq]',
                 'ODP'),
            'particulate matter formation no LT [disease incidence]':
                ('Particulate Matter Formation',
                 'impact on human health no LT',
                 '[disease incidence]',
                 'PM'),
            'photochemical oxidant formation: human health no LT [kg NMVOC-Eq]':
                ('Photochemical Oxidant Formation',
                 'tropospheric oxidant concentration increase no LT',
                 '[kg NMVOC-Eq]',
                 'POF'),
            'water use no LT [m3 world eq. deprived]':
                ('Water Use',
                 'user deprivation potential (deprivation-weighted water consumption) no LT',
                 '[m3 world eq. deprived]',
                 'WS')
        }

    # International Panel on Climate Change (IPCC) 2021:
    elif lcia_method == "'IPCC 2021'":

        lcia_transl_dict = {
            'climate change [kg C02-Eq]': ('Climate Change', 'global temperature change potential (GTP100)', '[kg C02-Eq]', 'GTP100'),
            'climate change [kg C02-Eq]': ('Climate Change', 'global temperature change potential (GTP50)', '[kg C02-Eq]', 'GTP50'),
            'climate change [kg C02-Eq]': ('Climate Change', 'global warming potential (GWP100)', '[kg C02-Eq]', 'GWP100'),
            'climate change [kg C02-Eq]': ('Climate Change', 'global warming potential (GWP20)', '[kg C02-Eq]', 'GWP20'),
            'climate change [kg C02-Eq]': ('Climate Change', 'global warming potential (GWP500)', '[kg C02-Eq]', 'GWP500')
        }

    else:

        raise KeyError(f"Translation dictionary for LCIA method '{lcia_method}' not found in lca_databases.py.")

    return lcia_transl_dict