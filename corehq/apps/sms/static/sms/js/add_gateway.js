hqDefine('sms/js/add_gateway', function() {
    var initialPageData = hqImport('hqwebapp/js/initial_page_data'),
        AddGatewayFormHandler = hqImport('add_gateway_form_handler').AddGatewayFormHandler;

    var gatewayFormHandler = new AddGatewayFormHandler({
        share_backend: initialPageData.get('form').give_other_domains_access.value,
        use_load_balancing: initialPageData.get('use_load_balancing'),
        phone_numbers: initialPageData.get('form').phone_numbers.value || '[]',
        phone_number_required_text: gettext('You must have at least one phone number.'),
    });

    $(function () {
        $('#add-gateway-form').koApplyBindings(gatewayFormHandler);
        gatewayFormHandler.init();
    });
});
