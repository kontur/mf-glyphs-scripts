from collections import Counter
import unicodedata as uni
from copy import copy

IGNORE_GLYPHS_OUTLINE = [
    'uni0000',
    'uni0002',
    'uni0009',
    'uni000A',
    'NULL',
    'null',
    '.null',
    'CR',
    'nbspace',
]


def find_duplicates(font_glyphs):
    '''Check if there are duplicate glyphs'''
    print '**Find Duplicate glyphs in selected font**'
    glyphs_count = Counter(font_glyphs)
    if len(set(glyphs_count.values())) >= 2:
        for glyph in glyphs_count:
            if glyphs_count[glyph] >= 2:
                print 'ERROR: %s duplicated\n' % glyph
    else:
        print 'PASS: No duplicate glyphs\n'


def find_00_glyphs(font_glyphs):
    print '**Find glyphs with suffix .00**'
    bad_glyphs = []
    for glyph in font_glyphs:
        if '.0' in glyph.name:
            bad_glyphs.append(glyph.name)

    if bad_glyphs:
        print 'ERROR: font contains %s\n' % ', '.join(bad_glyphs)
    else:
        print 'PASS: font contains no .00x glyphs\n'


def outlines_missing(font):
    '''Check if glyphs are missing outlines or composites.
    Only works on glyphs which have unicodes'''
    print '**Check Glyphs have outlines or components**'
    masters = font.masters

    for i, master in enumerate(masters):
        bad_glyphs = []
        for glyph in font.glyphs:

            if str(glyph.category) != 'Separator' and glyph.name not in IGNORE_GLYPHS_OUTLINE:
                if len(glyph.layers[i].paths) == 0:
                    if len(glyph.layers[i].components) == 0:
                        bad_glyphs.append(glyph.name)

        if bad_glyphs:
            for glyph in bad_glyphs:
                print "ERROR: %s master's %s should have outlines or components\n" % (master.name, glyph)            
        else:
            print "PASS: %s master's glyphs have components or outlines\n" % master.name

def find_duplicate_components(glyphs):
    '''Find duplicate components in the same glyph and share
    the same affine transformation.
    This happens when Glyphs generates a glyph like quotedblright.'''
    print '**Find duplicate components that share the same position/transformation.**'
    no_error = True
    for glyph in glyphs:
        for layer in glyph.layers:
            all_transformations = {}
            all_components = {}
            for component in layer.components:
                name = component.componentName
                if name not in all_components:
                    all_components[name] = []
                    all_transformations[name] = set()
                all_components[name].append(component)
                all_transformations[name].add(tuple(component.transform))
            for name, components in all_components.iteritems():
                transformations = all_transformations[name];
                if len(transformations) != len(components):
                    no_error = False
                    print ('ERROR: glyph {glyph} layer {layer}: {count_c} '
                        + 'components of {component} share {count_t} '
                        + 'transformations.\n    '
                        + 'All components of the same type must be positioned '
                        + 'differently.\n').format(
                                                glyph=glyph.name,
                                                layer=layer.name,
                                                count_c=len(components),
                                                component=name,
                                                count_t=len(transformations))
    if no_error:
        print 'PASS: no duplicate components share the same spot.\n'


def find_missing_components(glyphs, layers):
    """Check composites match GlyphsApp's GlyphData.xml

    .case suffixes are stripped during the check eg:
    acute.comb -> acute"""
    print '**Find glyphs which should have components**'
    component_map = {}
    bad_glyphs = []

    for glyph in glyphs:
        component_map[glyph.name] = []
        try:
            for component in glyph.glyphInfo.components:
                    component_map[glyph.name].append(component.name.split('.')[0])
        except:
            all

    for glyph in glyphs:
        if glyph.category == 'Letter':
            for i, master in enumerate(layers):
                no_case_comp_names = set(g.componentName.split('.')[0] for
                                         g in glyph.layers[i].components)
                if set(component_map[glyph.name]) - no_case_comp_names:
                    bad_glyphs.append(
                        (glyph.name,
                         glyph.layers[i].name,
                         set(component_map[glyph.name]) - no_case_comp_names)
                    )

    if bad_glyphs:
        for glyph, layer, comps in bad_glyphs:
            print "WARNING: %s %s missing '%s'" % (glyph, layer, ', '.join(comps))
        print '\n'
    else:
        print "PASS: Fonts have the same components as GlyphData.xml\n"


def _remove_overlaps(glyph):
    '''remove path overlaps for all layers'''
    for layer in glyph.layers:
        layer.removeOverlap()
    return glyph


def font_glyphs_contours(font):
    '''Return nested dictionary:
        layer[glyph] = contour_count
        Reg:
            A: 2
            B: 3
        Bold:
            A: 2
            B: 3
    '''
    glyphs = {}

    masters = font.masters
    for master in masters:
        if master.name not in glyphs:
            glyphs[master.name] = {}
        for glyph in font.glyphs:
            glyph_cp = copy(glyph)
            glyph_no_overlap = _remove_overlaps(glyph_cp)
            glyph_contours = len(glyph_no_overlap.layers[master.id].paths)
            glyphs[master.name][glyph.name] = glyph_contours
    return glyphs


def font_glyphs_compatible(glyph_paths_count):
    '''Preflight master compatbility check'''
    good_glyphs = {}
    bad_glyphs = set()
    for master1 in glyph_paths_count:
        for master2 in glyph_paths_count:
            glyphs1 = glyph_paths_count[master1]
            glyphs2 = glyph_paths_count[master2]
            shared_glyphs = set(glyphs1) & set(glyphs2)
            for glyph in shared_glyphs:
                if glyphs1[glyph] == glyphs2[glyph]:
                    good_glyphs[glyph] = glyphs1[glyph]
                else:
                    bad_glyphs.add(glyph)
    if bad_glyphs:
        for glyph in bad_glyphs:
            print 'WARNING: %s not consistent, check masters' % glyph
        print '\n'
    return good_glyphs


def instance_compatibility(font):
    '''Check if instances share the same path count as their masters.
    This is useful to check if the deiresis have merged into a single
    dot.'''
    print '**Check glyph instances have same amount of paths**'
    glyph_paths_count = font_glyphs_contours(font)
    compatible_glyphs = font_glyphs_compatible(glyph_paths_count)

    instances = font.instances

    bad_glyphs = []
    for instance in instances:
        faux_font = instance.interpolatedFont
        for glyph in compatible_glyphs:
            try:
                faux_glyph = faux_font.glyphs[glyph].layers[0]
                faux_glyph.removeOverlap()
                if len(faux_glyph.paths) != compatible_glyphs[glyph]:
                    print 'WARNING: %s, %s %s Instance has %s, whilst masters have %s' % (
                        glyph,
                        instance.width,
                        instance.name,
                        len(faux_glyph.paths),
                        compatible_glyphs[glyph]
                    )
                    bad_glyphs.append(glyph)
            except:
                all
    print '\n'
    if not bad_glyphs:
        print 'PASS: Instances and Masters share same contour count\n'
