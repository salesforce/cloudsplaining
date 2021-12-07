class Cloudsplaining < Formula
  include Language::Python::Virtualenv

  desc "Shiny new formula"
  homepage "https://github.com/salesforce/cloudsplaining"
  url "https://files.pythonhosted.org/packages/a9/51/93e2e0dd768bcf2df760942e4154b859c1512ed92dc5a6904c3b87a86a64/cloudsplaining-0.4.9.tar.gz"
  sha256 "42bbbf939490c17eb8fb2a98d199bd8ae3e07f10723affcdfcf557f57a9c64eb"

  depends_on "python3"

  resource "beautifulsoup4" do
    url "https://files.pythonhosted.org/packages/a1/69/daeee6d8f22c997e522cdbeb59641c4d31ab120aba0f2c799500f7456b7e/beautifulsoup4-4.10.0.tar.gz"
    sha256 "c23ad23c521d818955a4151a67d81580319d4bf548d3d49f4223ae041ff98891"
  end

  resource "boto3" do
    url "https://files.pythonhosted.org/packages/95/a7/413caa923eff54277fa48f312c2202441ed8ce57c5bf135af9b700e0994d/boto3-1.20.21.tar.gz"
    sha256 "2fb05cbe81b9ce11d9394fc6c4ffa5fd1cceb114dc1d2887dc61081707e44522"
  end

  resource "botocore" do
    url "https://files.pythonhosted.org/packages/7b/e6/b3aaa252218b0d4c6699de08d1daf94f90f320e3389e46b1286e18410c37/botocore-1.23.21.tar.gz"
    sha256 "d7f8e82cba38aa1e66015cab0a5ca3204503e90afc4695e97228e28329a14c04"
  end

  resource "cached-property" do
    url "https://files.pythonhosted.org/packages/61/2c/d21c1c23c2895c091fa7a91a54b6872098fea913526932d21902088a7c41/cached-property-1.5.2.tar.gz"
    sha256 "9fa5755838eecbb2d234c3aa390bd80fbd3ac6b6869109bfc1b499f7bd89a130"
  end

  resource "certifi" do
    url "https://files.pythonhosted.org/packages/6c/ae/d26450834f0acc9e3d1f74508da6df1551ceab6c2ce0766a593362d6d57f/certifi-2021.10.8.tar.gz"
    sha256 "78884e7c1d4b00ce3cea67b44566851c4343c120abd683433ce934a68ea58872"
  end

  resource "charset-normalizer" do
    url "https://files.pythonhosted.org/packages/68/e4/e014e7360fc6d1ccc507fe0b563b4646d00e0d4f9beec4975026dd15850b/charset-normalizer-2.0.9.tar.gz"
    sha256 "b0b883e8e874edfdece9c28f314e3dd5badf067342e42fb162203335ae61aa2c"
  end

  resource "click" do
    url "https://files.pythonhosted.org/packages/f4/09/ad003f1e3428017d1c3da4ccc9547591703ffea548626f47ec74509c5824/click-8.0.3.tar.gz"
    sha256 "410e932b050f5eed773c4cda94de75971c89cdb3155a72a0831139a79e5ecb5b"
  end

  resource "click-option-group" do
    url "https://files.pythonhosted.org/packages/3c/86/5de6d909d9dcc85627a178788ec3e8c3ef81cda175badb48ad0bb582628d/click-option-group-0.5.3.tar.gz"
    sha256 "a6e924f3c46b657feb5b72679f7e930f8e5b224b766ab35c91ae4019b4e0615e"
  end

  resource "contextlib2" do
    url "https://files.pythonhosted.org/packages/c7/13/37ea7805ae3057992e96ecb1cffa2fa35c2ef4498543b846f90dd2348d8f/contextlib2-21.6.0.tar.gz"
    sha256 "ab1e2bfe1d01d968e1b7e8d9023bc51ef3509bba217bb730cee3827e1ee82869"
  end

  resource "idna" do
    url "https://files.pythonhosted.org/packages/62/08/e3fc7c8161090f742f504f40b1bccbfc544d4a4e09eb774bf40aafce5436/idna-3.3.tar.gz"
    sha256 "9d643ff0a55b762d5cdb124b8eaa99c66322e2157b69160bc32796e824360e6d"
  end

  resource "importlib-metadata" do
    url "https://files.pythonhosted.org/packages/2e/6d/4508b1922b1610f6646fd95681fa1b0c092df35ec14018218f4638b7342a/importlib_metadata-4.8.2.tar.gz"
    sha256 "75bdec14c397f528724c1bfd9709d660b33a4d2e77387a3358f20b848bb5e5fb"
  end

  resource "Jinja2" do
    url "https://files.pythonhosted.org/packages/91/a5/429efc6246119e1e3fbf562c00187d04e83e54619249eb732bb423efa6c6/Jinja2-3.0.3.tar.gz"
    sha256 "611bb273cd68f3b993fabdc4064fc858c5b47a973cb5aa7999ec1ba405c87cd7"
  end

  resource "jmespath" do
    url "https://files.pythonhosted.org/packages/3c/56/3f325b1eef9791759784aa5046a8f6a1aff8f7c898a2e34506771d3b99d8/jmespath-0.10.0.tar.gz"
    sha256 "b85d0567b8666149a93172712e68920734333c0ce7e89b78b3e987f71e5ed4f9"
  end

  resource "Markdown" do
    url "https://files.pythonhosted.org/packages/15/06/d60f21eda994b044cbd496892d4d4c5c708aa597fcaded7d421513cb219b/Markdown-3.3.6.tar.gz"
    sha256 "76df8ae32294ec39dcf89340382882dfa12975f87f45c3ed1ecdb1e8cefc7006"
  end

  resource "MarkupSafe" do
    url "https://files.pythonhosted.org/packages/bf/10/ff66fea6d1788c458663a84d88787bae15d45daa16f6b3ef33322a51fc7e/MarkupSafe-2.0.1.tar.gz"
    sha256 "594c67807fb16238b30c44bdf74f36c02cdf22d1c8cda91ef8a0ed8dabf5620a"
  end

  resource "policy-sentry" do
    url "https://files.pythonhosted.org/packages/bb/c4/2a0958a730127c5da0eb2a7220f8d93dacdb47a5a8bce1471fd5bba2fb14/policy_sentry-0.11.19.tar.gz"
    sha256 "45921ada569a8619b9254994ff72b64c8c5f58ad08e4a067779d61fbbe57c341"
  end

  resource "python-dateutil" do
    url "https://files.pythonhosted.org/packages/4c/c4/13b4776ea2d76c115c1d1b84579f3764ee6d57204f6be27119f13a61d0a9/python-dateutil-2.8.2.tar.gz"
    sha256 "0123cacc1627ae19ddf3c27a5de5bd67ee4586fbdd6440d9748f8abb483d3e86"
  end

  resource "PyYAML" do
    url "https://files.pythonhosted.org/packages/36/2b/61d51a2c4f25ef062ae3f74576b01638bebad5e045f747ff12643df63844/PyYAML-6.0.tar.gz"
    sha256 "68fb519c14306fec9720a2a5b45bc9f0c8d1b9c72adf45c37baedfcd949c35a2"
  end

  resource "requests" do
    url "https://files.pythonhosted.org/packages/e7/01/3569e0b535fb2e4a6c384bdbed00c55b9d78b5084e0fb7f4d0bf523d7670/requests-2.26.0.tar.gz"
    sha256 "b8aa58f8cf793ffd8782d3d8cb19e66ef36f7aba4353eec859e74678b01b07a7"
  end

  resource "s3transfer" do
    url "https://files.pythonhosted.org/packages/88/ef/4d1b3f52ae20a7e72151fde5c9f254cd83f8a49047351f34006e517e1655/s3transfer-0.5.0.tar.gz"
    sha256 "50ed823e1dc5868ad40c8dc92072f757aa0e653a192845c94a3b676f4a62da4c"
  end

  resource "schema" do
    url "https://files.pythonhosted.org/packages/4e/e8/01e1b46d9e04cdaee91c9c736d9117304df53361a191144c8eccda7f0ee9/schema-0.7.5.tar.gz"
    sha256 "f06717112c61895cabc4707752b88716e8420a8819d71404501e114f91043197"
  end

  resource "six" do
    url "https://files.pythonhosted.org/packages/71/39/171f1c67cd00715f190ba0b100d606d440a28c93c7714febeca8b79af85e/six-1.16.0.tar.gz"
    sha256 "1e61c37477a1626458e36f7b1d82aa5c9b094fa4802892072e49de9c60c4c926"
  end

  resource "soupsieve" do
    url "https://files.pythonhosted.org/packages/e1/25/a3005eedafb34e1258458e8a4b94900a60a41a2b4e459e0e19631648a2a0/soupsieve-2.3.1.tar.gz"
    sha256 "b8d49b1cd4f037c7082a9683dfa1801aa2597fb11c3a1155b7a5b94829b4f1f9"
  end

  resource "typing-extensions" do
    url "https://files.pythonhosted.org/packages/0d/4a/60ba3706797b878016f16edc5fbaf1e222109e38d0fa4d7d9312cb53f8dd/typing_extensions-4.0.1.tar.gz"
    sha256 "4ca091dea149f945ec56afb48dae714f21e8692ef22a395223bcd328961b6a0e"
  end

  resource "urllib3" do
    url "https://files.pythonhosted.org/packages/80/be/3ee43b6c5757cabea19e75b8f46eaf05a2f5144107d7db48c7cf3a864f73/urllib3-1.26.7.tar.gz"
    sha256 "4987c65554f7a2dbf30c18fd48778ef124af6fab771a377103da0585e2336ece"
  end

  resource "zipp" do
    url "https://files.pythonhosted.org/packages/02/bf/0d03dbdedb83afec081fefe86cae3a2447250ef1a81ac601a9a56e785401/zipp-3.6.0.tar.gz"
    sha256 "71c644c5369f4a6e07636f0aa966270449561fcea2e3d6747b8d23efaa9d7832"
  end

  def install
    virtualenv_create(libexec, "python3")
    virtualenv_install_with_resources
  end

  test do
    false
  end
end
