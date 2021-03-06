from StarFile import StarBlock, StarFile, StarList, StarDict

# An alternative specification for the Cif Parser, based on Yapps2
# by Amit Patel (http://theory.stanford.edu/~amitp/Yapps)
#
# helper code: we define our match tokens
lastval = ''


def monitor(location, value):
    global lastval
    # print 'At %s: %s' % (location,`value`)
    lastval = `value`
    return value


# Strip extras gets rid of leading and trailing whitespace, and
# semicolons.
def stripextras(value):
    from StarFile import remove_line_folding, remove_line_prefix
    # we get rid of semicolons and leading/trailing terminators etc.
    import re
    jj = re.compile("[\n\r\f \t\v]*")
    semis = re.compile("[\n\r\f \t\v]*[\n\r\f]\n*;")
    cut = semis.match(value)
    if cut:  # we have a semicolon-delimited string
        nv = value[cut.end():len(value) - 2]
        try:
            if nv[-1] == '\r': nv = nv[:-1]
        except IndexError:  # empty data value
            pass
        # apply protocols
        nv = remove_line_prefix(nv)
        nv = remove_line_folding(nv)
        return nv
    else:
        cut = jj.match(value)
        if cut:
            return stripstring(value[cut.end():])
        return value


# helper function to get rid of inverted commas etc.

def stripstring(value):
    if value:
        if value[0] == '\'' and value[-1] == '\'':
            return value[1:-1]
        if value[0] == '"' and value[-1] == '"':
            return value[1:-1]
    return value


# helper function to get rid of triple quotes
def striptriple(value):
    if value:
        if value[:3] == '"""' and value[-3:] == '"""':
            return value[3:-3]
        if value[:3] == "'''" and value[-3:] == "'''":
            return value[3:-3]
    return value


# helper function to populate a StarBlock given a list of names
# and values .   
#
# Note that there may be an empty list at the very end of our itemlists,
# so we remove that if necessary.
#

def makeloop(target_block, loopdata):
    loop_seq, itemlists = loopdata
    if itemlists[-1] == []: itemlists.pop(-1)
    # print 'Making loop with %s' % `itemlists`
    step_size = len(loop_seq)
    for col_no in range(step_size):
        target_block.AddItem(loop_seq[col_no], itemlists[col_no::step_size], precheck=True)
    # print 'Makeloop constructed %s' % `loopstructure`
    # now construct the loop
    try:
        target_block.CreateLoop(loop_seq)  # will raise ValueError on problem
    except ValueError:
        error_string = 'Incorrect number of loop values for loop containing %s' % `loop_seq`
        print >> sys.stderr, error_string
        raise ValueError, error_string


# return an object with the appropriate amount of nesting
def make_empty(nestlevel):
    gd = []
    for i in range(1, nestlevel):
        gd = [gd]
    return gd


# this function updates a dictionary first checking for name collisions,
# which imply that the CIF is invalid.  We need case insensitivity for
# names. 

# Unfortunately we cannot check loop item contents against non-loop contents
# in a non-messy way during parsing, as we may not have easy access to previous
# key value pairs in the context of our call (unlike our built-in access to all 
# previous loops).
# For this reason, we don't waste time checking looped items against non-looped
# names during parsing of a data block.  This would only match a subset of the
# final items.   We do check against ordinary items, however.
#
# Note the following situations:
# (1) new_dict is empty -> we have just added a loop; do no checking
# (2) new_dict is not empty -> we have some new key-value pairs
#
def cif_update(old_dict, new_dict, loops):
    old_keys = map(lambda a: a.lower(), old_dict.keys())
    if new_dict != {}:  # otherwise we have a new loop
        # print 'Comparing %s to %s' % (`old_keys`,`new_dict.keys()`)
        for new_key in new_dict.keys():
            if new_key.lower() in old_keys:
                raise CifError, "Duplicate dataname or blockname %s in input file" % new_key
            old_dict[new_key] = new_dict[new_key]


#
# this takes two lines, so we couldn't fit it into a one line execution statement...
def order_update(order_array, new_name):
    order_array.append(new_name)
    return new_name


# and finally...turn a sequence into a python dict (thanks to Stackoverflow)
def pairwise(iterable):
    itnext = iter(iterable).next
    while 1:
        yield itnext(), itnext()


# Begin -- grammar generated by Yapps
import sys, re
import yapps3_compiled_rt as yappsrt


class StarParserScanner(yappsrt.Scanner):
    patterns = [
        ('":"', re.compile(':')),
        ('","', re.compile(',')),
        ('([ \t\n\r](?!;))|[ \t]', re.compile('([ \t\n\r](?!;))|[ \t]')),
        ('(#.*[\n\r](?!;))|(#.*)', re.compile('(#.*[\n\r](?!;))|(#.*)')),
        ('LBLOCK', re.compile('(L|l)(O|o)(O|o)(P|p)_')),
        ('GLOBAL', re.compile('(G|g)(L|l)(O|o)(B|b)(A|a)(L|l)_')),
        ('STOP', re.compile('(S|s)(T|t)(O|o)(P|p)_')),
        ('save_heading', re.compile(
            '(S|s)(A|a)(V|v)(E|e)_[][!%&\\(\\)*+,./:<=>?@0-9A-Za-z\\\\^`{}\\|~"#$\';_\\u00A0-\\uD7FF\\uE000-\\uFDCF\\uFDF0-\\uFFFD-]+')),
        ('save_end', re.compile('(S|s)(A|a)(V|v)(E|e)_')),
        ('data_name',
         re.compile(u'_[][!%&\\(\\)*+,./:<=>?@0-9A-Za-z\\\\^`{}\\|~"#$\';_\xa0-\ud7ff\ue000-\ufdcf\ufdf0-\ufffd-]+')),
        ('data_heading', re.compile(
            u'(D|d)(A|a)(T|t)(A|a)_[][!%&\\(\\)*+,./:<=>?@0-9A-Za-z\\\\^`{}\\|~"#$\';_\xa0-\ud7ff\ue000-\ufdcf\ufdf0-\ufffd-]+')),
        ('start_sc_line', re.compile('(\n|\r\n);([^\n\r])*(\r\n|\r|\n)+')),
        ('sc_line_of_text', re.compile('[^;\r\n]([^\r\n])*(\r\n|\r|\n)+')),
        ('end_sc_line', re.compile(';')),
        ('c_c_b', re.compile('\\}')),
        ('o_c_b', re.compile('\\{')),
        ('c_s_b', re.compile('\\]')),
        ('o_s_b', re.compile('\\[')),
        ('dat_val_internal_sq', re.compile('\\[([^\\s\\[\\]]*)\\]')),
        ('triple_quote_data_value', re.compile('(?s)\'\'\'.*?\'\'\'|""".*"""')),
        ('single_quote_data_value', re.compile('\'([^\n\r\x0c\'])*\'+|"([^\n\r"])*"+')),
        ('END', re.compile('$')),
        ('data_value_1', re.compile(
            '((?!(((S|s)(A|a)(V|v)(E|e)_[^\\s]*)|((G|g)(L|l)(O|o)(B|b)(A|a)(L|l)_[^\\s]*)|((S|s)(T|t)(O|o)(P|p)_[^\\s]*)|((D|d)(A|a)(T|t)(A|a)_[^\\s]*)))[^\\s"#$\',_\\{\\}\\[\\]][^\\s,\\{\\}\\[\\]]*)')),
    ]

    def __init__(self, str):
        yappsrt.Scanner.__init__(self, None, ['([ \t\n\r](?!;))|[ \t]', '(#.*[\n\r](?!;))|(#.*)'], str)


class StarParser(yappsrt.Parser):
    Context = yappsrt.Context

    def input(self, prepared, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'input', [prepared])
        _token = self._peek('END', 'data_heading')
        if _token == 'data_heading':
            dblock = self.dblock(prepared, _context)
            allblocks = prepared;
            allblocks.merge_fast(dblock)
            while self._peek('END', 'data_heading') == 'data_heading':
                dblock = self.dblock(prepared, _context)
                allblocks.merge_fast(dblock)
            if self._peek() not in ['END', 'data_heading']:
                raise yappsrt.SyntaxError(charpos=self._scanner.get_prev_char_pos(), context=_context,
                                          msg='Need one of ' + ', '.join(['END', 'data_heading']))
            END = self._scan('END')
        else:  # == 'END'
            END = self._scan('END')
            allblocks = prepared
        return allblocks

    def dblock(self, prepared, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'dblock', [prepared])
        data_heading = self._scan('data_heading')
        heading = data_heading[5:];
        thisbc = StarFile(characterset='unicode', standard=prepared.standard);
        thisbc.NewBlock(heading, StarBlock(overwrite=False))
        while self._peek('save_heading', 'LBLOCK', 'data_name', 'save_end', 'END', 'data_heading') in ['save_heading',
                                                                                                       'LBLOCK',
                                                                                                       'data_name']:
            _token = self._peek('save_heading', 'LBLOCK', 'data_name')
            if _token != 'save_heading':
                dataseq = self.dataseq(thisbc[heading], _context)
            else:  # == 'save_heading'
                save_frame = self.save_frame(_context)
                thisbc.merge_fast(save_frame, parent=heading)
        if self._peek() not in ['save_heading', 'LBLOCK', 'data_name', 'save_end', 'END', 'data_heading']:
            raise yappsrt.SyntaxError(charpos=self._scanner.get_prev_char_pos(), context=_context,
                                      msg='Need one of ' + ', '.join(
                                          ['save_heading', 'LBLOCK', 'data_name', 'save_end', 'END', 'data_heading']))
        thisbc[heading].setmaxnamelength(thisbc[heading].maxnamelength);
        return (monitor('dblock', thisbc))

    def dataseq(self, starblock, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'dataseq', [starblock])
        data = self.data(starblock, _context)
        while self._peek('LBLOCK', 'data_name', 'save_heading', 'save_end', 'END', 'data_heading') in ['LBLOCK',
                                                                                                       'data_name']:
            data = self.data(starblock, _context)
        if self._peek() not in ['LBLOCK', 'data_name', 'save_heading', 'save_end', 'END', 'data_heading']:
            raise yappsrt.SyntaxError(charpos=self._scanner.get_prev_char_pos(), context=_context,
                                      msg='Need one of ' + ', '.join(
                                          ['LBLOCK', 'data_name', 'save_heading', 'save_end', 'END', 'data_heading']))

    def data(self, currentblock, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'data', [currentblock])
        _token = self._peek('LBLOCK', 'data_name')
        if _token == 'LBLOCK':
            top_loop = self.top_loop(_context)
            makeloop(currentblock, top_loop)
        else:  # == 'data_name'
            datakvpair = self.datakvpair(_context)
            currentblock.AddItem(datakvpair[0], datakvpair[1], precheck=False)

    def datakvpair(self, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'datakvpair', [])
        data_name = self._scan('data_name')
        data_value = self.data_value(_context)
        return [data_name, data_value]

    def data_value(self, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'data_value', [])
        _token = self._peek('data_value_1', 'triple_quote_data_value', 'single_quote_data_value', 'start_sc_line',
                            'o_s_b', 'o_c_b')
        if _token == 'data_value_1':
            data_value_1 = self._scan('data_value_1')
            thisval = data_value_1
        elif _token not in ['start_sc_line', 'o_s_b', 'o_c_b']:
            delimited_data_value = self.delimited_data_value(_context)
            thisval = stripstring(delimited_data_value)
        elif _token == 'start_sc_line':
            sc_lines_of_text = self.sc_lines_of_text(_context)
            thisval = stripextras(sc_lines_of_text)
        else:  # in ['o_s_b', 'o_c_b']
            bracket_expression = self.bracket_expression(_context)
            thisval = bracket_expression
        return monitor('data_value', thisval)

    def delimited_data_value(self, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'delimited_data_value', [])
        _token = self._peek('triple_quote_data_value', 'single_quote_data_value')
        if _token == 'triple_quote_data_value':
            triple_quote_data_value = self._scan('triple_quote_data_value')
            thisval = striptriple(triple_quote_data_value)
        else:  # == 'single_quote_data_value'
            single_quote_data_value = self._scan('single_quote_data_value')
            thisval = stripstring(single_quote_data_value)
        return thisval

    def sc_lines_of_text(self, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'sc_lines_of_text', [])
        start_sc_line = self._scan('start_sc_line')
        lines = start_sc_line
        while self._peek('end_sc_line', 'sc_line_of_text') == 'sc_line_of_text':
            sc_line_of_text = self._scan('sc_line_of_text')
            lines = lines + sc_line_of_text
        if self._peek() not in ['end_sc_line', 'sc_line_of_text']:
            raise yappsrt.SyntaxError(charpos=self._scanner.get_prev_char_pos(), context=_context,
                                      msg='Need one of ' + ', '.join(['sc_line_of_text', 'end_sc_line']))
        end_sc_line = self._scan('end_sc_line')
        return monitor('sc_line_of_text', lines + end_sc_line)

    def bracket_expression(self, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'bracket_expression', [])
        _token = self._peek('o_s_b', 'o_c_b')
        if _token == 'o_s_b':
            square_bracket_expr = self.square_bracket_expr(_context)
            return square_bracket_expr
        else:  # == 'o_c_b'
            curly_bracket_expr = self.curly_bracket_expr(_context)
            return curly_bracket_expr

    def top_loop(self, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'top_loop', [])
        LBLOCK = self._scan('LBLOCK')
        loopfield = self.loopfield(_context)
        loopvalues = self.loopvalues(_context)
        return loopfield, loopvalues

    def loopfield(self, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'loopfield', [])
        loop_seq = []
        while self._peek('data_name', 'data_value_1', 'triple_quote_data_value', 'single_quote_data_value',
                         'start_sc_line', 'o_s_b', 'o_c_b') == 'data_name':
            data_name = self._scan('data_name')
            loop_seq.append(data_name)
        if self._peek() not in ['data_name', 'data_value_1', 'triple_quote_data_value', 'single_quote_data_value',
                                'start_sc_line', 'o_s_b', 'o_c_b']:
            raise yappsrt.SyntaxError(charpos=self._scanner.get_prev_char_pos(), context=_context,
                                      msg='Need one of ' + ', '.join(
                                          ['data_name', 'data_value_1', 'triple_quote_data_value',
                                           'single_quote_data_value', 'start_sc_line', 'o_s_b', 'o_c_b']))
        return loop_seq

    def loopvalues(self, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'loopvalues', [])
        data_value = self.data_value(_context)
        dataloop = [data_value]
        while self._peek('data_value_1', 'triple_quote_data_value', 'single_quote_data_value', 'start_sc_line', 'o_s_b',
                         'o_c_b', 'LBLOCK', 'data_name', 'save_heading', 'save_end', 'END', 'data_heading') in [
            'data_value_1', 'triple_quote_data_value', 'single_quote_data_value', 'start_sc_line', 'o_s_b', 'o_c_b']:
            data_value = self.data_value(_context)
            dataloop.append(monitor('loopval', data_value))
        if self._peek() not in ['data_value_1', 'triple_quote_data_value', 'single_quote_data_value', 'start_sc_line',
                                'o_s_b', 'o_c_b', 'LBLOCK', 'data_name', 'save_heading', 'save_end', 'END',
                                'data_heading']:
            raise yappsrt.SyntaxError(charpos=self._scanner.get_prev_char_pos(), context=_context,
                                      msg='Need one of ' + ', '.join(
                                          ['data_value_1', 'triple_quote_data_value', 'single_quote_data_value',
                                           'start_sc_line', 'o_s_b', 'o_c_b', 'LBLOCK', 'data_name', 'save_heading',
                                           'save_end', 'END', 'data_heading']))
        return dataloop

    def save_frame(self, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'save_frame', [])
        save_heading = self._scan('save_heading')
        savehead = save_heading[5:];
        savebc = StarFile();
        savebc.NewBlock(savehead, StarBlock(overwrite=False))
        while self._peek('save_end', 'save_heading', 'LBLOCK', 'data_name', 'END', 'data_heading') in ['save_heading',
                                                                                                       'LBLOCK',
                                                                                                       'data_name']:
            _token = self._peek('save_heading', 'LBLOCK', 'data_name')
            if _token != 'save_heading':
                dataseq = self.dataseq(savebc[savehead], _context)
            else:  # == 'save_heading'
                save_frame = self.save_frame(_context)
                savebc.merge_fast(save_frame, parent=savehead)
        if self._peek() not in ['save_end', 'save_heading', 'LBLOCK', 'data_name', 'END', 'data_heading']:
            raise yappsrt.SyntaxError(charpos=self._scanner.get_prev_char_pos(), context=_context,
                                      msg='Need one of ' + ', '.join(
                                          ['save_end', 'save_heading', 'LBLOCK', 'data_name', 'END', 'data_heading']))
        save_end = self._scan('save_end')
        return monitor('save_frame', savebc)

    def square_bracket_expr(self, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'square_bracket_expr', [])
        o_s_b = self._scan('o_s_b')
        this_list = []
        while self._peek('c_s_b', 'data_value_1', '","', 'triple_quote_data_value', 'single_quote_data_value',
                         'start_sc_line', 'o_s_b', 'o_c_b') not in ['c_s_b', '","']:
            data_value = self.data_value(_context)
            this_list.append(data_value)
            while self._peek('","', 'data_value_1', 'c_s_b', 'triple_quote_data_value', 'single_quote_data_value',
                             'start_sc_line', 'o_s_b', 'o_c_b') == '","':
                self._scan('","')
                data_value = self.data_value(_context)
                this_list.append(data_value)
            if self._peek() not in ['","', 'data_value_1', 'c_s_b', 'triple_quote_data_value',
                                    'single_quote_data_value', 'start_sc_line', 'o_s_b', 'o_c_b']:
                raise yappsrt.SyntaxError(charpos=self._scanner.get_prev_char_pos(), context=_context,
                                          msg='Need one of ' + ', '.join(
                                              ['","', 'data_value_1', 'c_s_b', 'triple_quote_data_value',
                                               'single_quote_data_value', 'start_sc_line', 'o_s_b', 'o_c_b']))
        if self._peek() not in ['c_s_b', 'data_value_1', '","', 'triple_quote_data_value', 'single_quote_data_value',
                                'start_sc_line', 'o_s_b', 'o_c_b']:
            raise yappsrt.SyntaxError(charpos=self._scanner.get_prev_char_pos(), context=_context,
                                      msg='Need one of ' + ', '.join(
                                          ['data_value_1', 'c_s_b', 'triple_quote_data_value',
                                           'single_quote_data_value', 'start_sc_line', '","', 'o_s_b', 'o_c_b']))
        c_s_b = self._scan('c_s_b')
        return StarList(this_list)

    def curly_bracket_expr(self, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'curly_bracket_expr', [])
        o_c_b = self._scan('o_c_b')
        table_as_list = []
        while self._peek('c_c_b', 'triple_quote_data_value', 'single_quote_data_value', '","') in [
            'triple_quote_data_value', 'single_quote_data_value']:
            delimited_data_value = self.delimited_data_value(_context)
            table_as_list = [delimited_data_value]
            self._scan('":"')
            data_value = self.data_value(_context)
            table_as_list.append(data_value)
            while self._peek('","', 'triple_quote_data_value', 'single_quote_data_value', 'c_c_b') == '","':
                self._scan('","')
                delimited_data_value = self.delimited_data_value(_context)
                table_as_list.append(delimited_data_value)
                self._scan('":"')
                data_value = self.data_value(_context)
                table_as_list.append(data_value)
            if self._peek() not in ['","', 'triple_quote_data_value', 'single_quote_data_value', 'c_c_b']:
                raise yappsrt.SyntaxError(charpos=self._scanner.get_prev_char_pos(), context=_context,
                                          msg='Need one of ' + ', '.join(
                                              ['","', 'triple_quote_data_value', 'single_quote_data_value', 'c_c_b']))
        if self._peek() not in ['c_c_b', 'triple_quote_data_value', 'single_quote_data_value', '","']:
            raise yappsrt.SyntaxError(charpos=self._scanner.get_prev_char_pos(), context=_context,
                                      msg='Need one of ' + ', '.join(
                                          ['triple_quote_data_value', 'single_quote_data_value', 'c_c_b', '","']))
        c_c_b = self._scan('c_c_b')
        return StarDict(pairwise(table_as_list))


def parse(rule, text):
    P = StarParser(StarParserScanner(text))
    return yappsrt.wrap_error_reporter(P, rule)

# End -- grammar generated by Yapps
