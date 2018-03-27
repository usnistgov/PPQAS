xml_string ='''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE questionnaire SYSTEM "file:/C:/Users/cpaulsen/Documents/passwords/Survey%20Schema/passwordpolicy011014%20%20template.dtd">
<!-- .dtd location needs to be updated if file is moved -->
<questionnaire xmlns="ppt">
  <title>Password Policy Survey Tool</title>
  <xmlversion>010914 ugly</xmlversion>
  <qaversion>30oct2013v1</qaversion>
  <BNFversion>KevinV1</BNFversion>

  <navigation>
    <next>Next Page - {"attribute":"title"}</next>

    <back>Go Back to {"attribute":"title"}</back>
  </navigation>

  <errors>
    <validation type=">0 options">"Please select at least one option"</validation>
    <validation type="1-50">"Please enter a number between 1 and 50"</validation>
  </errors>

  <index>
    <group level="1" title="Communicate" comment_ref="c_1" next="Next Page - Creating Passwords" back="Home"> <!-- to be used when this level of grouping is desired -->
      <page title="Who" comment_ref="c_2" next="Next Page - Any Method" back="Home"> <!-- this element, but not the questions within, should be ignored if we don't want to do individual pages-->
        <include qref="1"></include>
        <include qref="1.1"></include>
      </page>
      <group  level="2" title="How" comment_ref="c_3">
        <page title="Any Method" comment_ref="c_4">
          <instructions><![CDATA[Text for instructions<br> for this page would go here and shown only when pages are shown]]></instructions>
          <include qref="2"></include>
          <include qref="2.1"></include>
        </page>
      </group>
    </group>
  </index>

  <questions>
    <category title="Communicate">
      <text>The password policy may tell users whether or not they can provide their passwords to other people, under particular circumstances.</text>

      <question id="1">
        <text>Does the policy identify people with whom users &lt;b&gt;may not&lt;/b&gt; communicate or share passwords?</text>
        <response type="select one">
          <option id="1.A">
            <text>Yes</text>
          </option>
          <option id="1.B">
            <text>No</text>
          </option>
        </response>
      </question>

      <question id="1.1" display_when="1.A">
        <!-- The "display when" attribute indicates that this question should only be displayed if that option is selected.-->
        <text>The policy states the following about not communicating or sharing passwords(select one)</text>
        <response type="select one">
          <option id="1.1.A">
            <text>The policy prohibits communicating or sharing passwords with &lt;b&gt;anyone&lt;/b&gt;.</text>
            <BNF_mapping id="bnf_1">Users must not communicate passwords to anyone</BNF_mapping>
            <!-- to map to BNF; can use exact phrase or a serial number system -->
          </option>
          <option id="1.1.B">
            <text>The policy prohibits communicating or sharing passwords with a &lt;b&gt;third party&lt;/b&gt;.</text>
            <BNF_mapping id="bnf_2">Users must not communicate  passwords to a third party</BNF_mapping>
          </option>
          <option id="1.1.C">
            <text>The policy recommends against communicating or sharing passwords with &lt;b&gt;anyone&lt;/b&gt;.</text>
            <BNF_mapping id="bnf_3">Users should not communicate passwords to anyone</BNF_mapping>
          </option>
          <option id="1.1.D">
            <text>The policy recommends against communicating or sharing passwords with &lt;b&gt;a third party&lt;/b&gt;.</text>
            <BNF_mapping id="bnf_3">Users should not communicate passwords to a third party</BNF_mapping>
          </option>
        </response>
      </question>
      <question id="2">
        <title>Communicate How</title>
        <text>The policy may specify the method (e.g., mail, email, Internet, phone, etc.) by which passwords may or may not be communicated or shared.</text>

        <question id="2.1">
          <title>Communicate "by any method"</title>
          <text>Does the policy make a general statement about communicating or sharing passwords "by any method" (or using similar words)?</text>
          <response type="select one">
            <option id="2.1.A">
              <text>Yes - the policy &lt;b&gt;prohibits&lt;/b&gt; communicating or sharing passwords &lt;b&gt;by any method&lt;/b&gt;.</text>
              <BNF_mapping>Users must not communicate passwords by any means</BNF_mapping>
            </option>
            <option id="2.1.B">
              <text>Yes - the policy &lt;b&gt;recommends against&lt;/b&gt; communicating or sharing passwords &lt;b&gt;by any method&lt;/b&gt;.</text>
              <BNF_mapping>Users should not communicate passwords by any means</BNF_mapping>
            </option>
            <option id="2.1.C">
              <text>No - the policy &lt;b&gt;does not&lt;/b&gt; make a general statement about communicating or sharing passwords &lt;b&gt;"by any method."&lt;/b&gt;</text>
            </option>
          </response>
        </question>
      </question>
    </category>
  </questions>
</questionnaire>
'''

xml_string_for_ids ='''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE questionnaire SYSTEM "file:/C:/Users/cpaulsen/Documents/passwords/Survey%20Schema/passwordpolicy011014%20%20template.dtd">
<!-- .dtd location needs to be updated if file is moved -->
<questionnaire xmlns="ppt">
  <title>Password Policy Survey Tool</title>
  <xmlversion>010914 ugly</xmlversion>
  <qaversion>30oct2013v1</qaversion>
  <BNFversion>KevinV1</BNFversion>

  <navigation>
    <next>Next Page - {"attribute":"title"}</next>

    <back>Go Back to {"attribute":"title"}</back>
  </navigation>

  <errors>
    <validation type=">0 options">"Please select at least one option"</validation>
    <validation type="1-50">"Please enter a number between 1 and 50"</validation>
  </errors>

  <index>
    <group level="1" title="Communicate" comment_ref="c_1" next="Next Page - Creating Passwords" back="Home"> <!-- to be used when this level of grouping is desired -->
      <page title="Who" comment_ref="c_2" next="Next Page - Any Method" back="Home"> <!-- this element, but not the questions within, should be ignored if we don't want to do individual pages-->
        <include qref="1"></include>
        <include qref="1.1"></include>
      </page>
      <group  level="2" title="How" comment_ref="c_3">
        <page title="Any Method" comment_ref="c_4">
          <instructions><![CDATA[Text for instructions<br> for this page would go here and shown only when pages are shown]]></instructions>
          <include qref="2"></include>
          <include qref="2.1"></include>
        </page>
      </group>
    </group>
  </index>

  <questions>
    <category title="Communicate">
      <text>The password policy may tell users whether or not they can provide their passwords to other people, under particular circumstances.</text>

      <question id="1">
        <text>Does the policy identify people with whom users &lt;b&gt;may not&lt;/b&gt; communicate or share passwords?</text>
        <response type="select one">
          <option id="1.A">
            <text>Yes</text>
          </option>
          <option id="1.B">
            <text>No</text>
          </option>
        </response>
      </question>
    </category>
  </questions>
</questionnaire>
'''
