const otherUtil = require('../util/other')
const glossaryUtil = require('../util/glossary')

let mocha = require('mocha');
let assert;
before(async () => { ({ assert } = await import('chai')); });
let it = mocha.it;

it("other.addSpacesInPascalCaseString: should insert spaces before capital letters in a PascalCase string", function () {
    var result = otherUtil.addSpacesInPascalCaseString("DataExfiltration");
    var expectedResult = "Data Exfiltration"
    assert(result === expectedResult);
    console.log(`Should equal Data Exfiltration: ${result}`);
});

it("other.convertStringToSnakeCase: should convert any string into snake case", function () {
    assert(otherUtil.convertStringToSnakeCase("camelCase") === "camel_case");
    assert(otherUtil.convertStringToSnakeCase("some text") === "some_text");
    assert(otherUtil.convertStringToSnakeCase("some-mixed_string With spaces_underscores-and-hyphens") === "some_mixed_string_with_spaces_underscores_and_hyphens");
    assert(otherUtil.convertStringToSnakeCase("AllThe-small Things'") === "all_the_small_things");
    assert(otherUtil.convertStringToSnakeCase("IAmListeningToFMWhileLoadingDifferentURLOnMyBrowserAndAlsoEditingSomeXMLAndHTML'") === "i_am_listening_to_fm_while_loading_different_url_on_my_browser_and_also_editing_some_xml_and_html");
});

it("other.convertStringToKebabCase: should convert any string into kebab-case", function () {
    assert(otherUtil.convertStringToKebabCase("kebabCase") === "kebab-case");
    assert(otherUtil.convertStringToKebabCase("some text") === "some-text");
    assert(otherUtil.convertStringToKebabCase("some-mixed_string With spaces_underscores-and-hyphens") === "some-mixed-string-with-spaces-underscores-and-hyphens");
    assert(otherUtil.convertStringToKebabCase("AllThe-small Things'") === "all-the-small-things");
    assert(otherUtil.convertStringToKebabCase("IAmListeningToFMWhileLoadingDifferentURLOnMyBrowserAndAlsoEditingSomeXMLAndHTML'") === "i-am-listening-to-fm-while-loading-different-url-on-my-browser-and-also-editing-some-xml-and-html");
});

it("other.convertStringToSpaceCase: should convert any string into Space Case", function () {
    console.log(otherUtil.convertStringToSpaceCase("spaceCase"));
    console.log(otherUtil.convertStringToSpaceCase("some text"));
    assert(otherUtil.convertStringToSpaceCase("spaceCase") === "Space Case");
    assert(otherUtil.convertStringToSpaceCase("some text") === "Some Text");
});

it("other.compareValues: array is sorted by band, in ascending order by default", function () {
    const singers = [
      { name: 'Steven Tyler', band: 'Aerosmith', born: 1948 },
      { name: 'Karen Carpenter', band: 'The Carpenters', born: 1950 },
      { name: 'Kurt Cobain', band: 'Nirvana', born: 1967 },
      { name: 'Stevie Nicks', band: 'Fleetwood Mac', born: 1948 },
    ];

    const expectedResult = [
      { name: 'Karen Carpenter', band: 'The Carpenters', born: 1950 },
      { name: 'Kurt Cobain', band: 'Nirvana', born: 1967 },
      { name: 'Steven Tyler', band: 'Aerosmith', born: 1948 },
      { name: 'Stevie Nicks', band: 'Fleetwood Mac', born: 1948 }
    ]

    var result = singers.sort(otherUtil.compareValues("name", "asc"));
    console.log(result)
    assert.deepStrictEqual(result, expectedResult)

    // var expectedResult = "Data Exfiltration"
    // assert(result === expectedResult);
    // console.log(`Should equal Data Exfiltration: ${result}`);
});

it("glossary.getRiskDetailsToDisplay", function() {
    console.log(glossaryUtil.getRiskDetailsToDisplay());
    for (let entry of glossaryUtil.getRiskDetailsToDisplay()) {
        console.log(entry.risk_type)
    }
})
