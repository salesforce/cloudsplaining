var otherUtil = require('../util/other')

let mocha = require('mocha');
let chai = require('chai');
let it = mocha.it;

it("other.addSpacesInPascalCaseString: should insert spaces before capital letters in a PascalCase string", function () {
    var result = otherUtil.addSpacesInPascalCaseString("DataExfiltration");
    var expectedResult = "Data Exfiltration"
    chai.assert(result === expectedResult);
    console.log(`Should equal Data Exfiltration: ${result}`);
});

it("other.convertStringToSnakeCase: should convert any string into snake case", function () {
    chai.assert(otherUtil.convertStringToSnakeCase("camelCase") === "camel_case");
    chai.assert(otherUtil.convertStringToSnakeCase("some text") === "some_text");
    chai.assert(otherUtil.convertStringToSnakeCase("some-mixed_string With spaces_underscores-and-hyphens") === "some_mixed_string_with_spaces_underscores_and_hyphens");
    chai.assert(otherUtil.convertStringToSnakeCase("AllThe-small Things'") === "all_the_small_things");
    chai.assert(otherUtil.convertStringToSnakeCase("IAmListeningToFMWhileLoadingDifferentURLOnMyBrowserAndAlsoEditingSomeXMLAndHTML'") === "i_am_listening_to_fm_while_loading_different_url_on_my_browser_and_also_editing_some_xml_and_html");
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
    chai.assert.deepStrictEqual(result, expectedResult)

    // var expectedResult = "Data Exfiltration"
    // chai.assert(result === expectedResult);
    // console.log(`Should equal Data Exfiltration: ${result}`);
});
