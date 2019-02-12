hqDefine('reach/js/filters/location_filter', [
    'jquery',
    'knockout',
    'underscore',
    'moment/moment',
    'hqwebapp/js/initial_page_data',
    'reach/js/utils/reach_utils',
    'reach/js/filters/location_model'
], function (
    $,
    ko,
    _,
    moment,
    initialPageData,
    reachUtils,
    locationModel
) {
    return {
        viewModel: function (params) {
            var self = {};
            self.slug = 'location-filter';
            self.hierarchyConfig = ko.observableArray();

            self.userRoleType = initialPageData.get('user_role_type');
            self.userLocationIds = initialPageData.get('user_location_ids');
            self.isWebUser = initialPageData.get('is_web_user');
            self.userLocationId = initialPageData.get('user_location_id');

            self.ministryList = [
                reachUtils.USERROLETYPES.MOHFW,
                reachUtils.USERROLETYPES.MWCD,
            ];

            self.selectedMinistry = ko.observable(self.userRoleType);

            self._initHierarchy = function () {
                var state = locationModel.locationModel({slug: 'state', name: 'State', parent: '', userLocationId: self.userLocationIds[0], postData: params.postData});
                var district = locationModel.locationModel({slug: 'district', name: 'District', parent: state, userLocationId: self.userLocationIds[1], postData: params.postData});
                state.setChild(district);
                if (self.selectedMinistry() === reachUtils.USERROLETYPES.MOHFW) {
                    var taluka = locationModel.locationModel({slug: 'taluka', name: 'Taluka', parent: district, userLocationId: self.userLocationIds[2], postData: params.postData});
                    var phc = locationModel.locationModel({slug: 'phc', name: 'Primary Health Centre (PHC)', parent: taluka, userLocationId: self.userLocationIds[3], postData: params.postData});
                    var sc = locationModel.locationModel({slug: 'sc', name: 'Sub-centre (SC)', parent: phc, userLocationId: self.userLocationIds[4], postData: params.postData});
                    var village = locationModel.locationModel({slug: 'village', name: 'Village', parent: sc, userLocationId: self.userLocationIds[5], postData: params.postData});
                    district.setChild((taluka));
                    taluka.setChild(phc);
                    phc.setChild(sc);
                    sc.setChild(village);
                    self.hierarchyConfig([
                        state,
                        district,
                        taluka,
                        phc,
                        sc,
                        village,
                    ]);
                } else {
                    var block = locationModel.locationModel({slug: 'block', name: 'Block', parent: district, userLocationId: self.userLocationIds[2], postData: params.postData});
                    var sector = locationModel.locationModel({slug: 'sector', name: 'Sector (Project)', parent: block, userLocationId: self.userLocationIds[3], postData: params.postData});
                    var awc = locationModel.locationModel({slug: 'awc', name: 'AWC', parent: sector, userLocationId: self.userLocationIds[4], postData: params.postData});
                    district.setChild((block));
                    block.setChild(sector);
                    sector.setChild(awc);
                    self.hierarchyConfig([
                        state,
                        district,
                        block,
                        sector,
                        awc,
                    ]);
                }

                params.localStorage.locationHierarchy(self.hierarchyConfig());
            };

            self._initHierarchy();

            params.filters[self.slug].resetFilters = function () {
                _.each(self.hierarchyConfig(), function (location) {
                    location.setDefaultOption();
                });
            };

            self.selectedMinistry.subscribe(function () {
                self._initHierarchy();
            });

            self.showMinistryFilter = function () {
                return self.isWebUser && self.userLocationId === null;
            };

            return self;
        },
        template: '<div data-bind="template: { name: \'location-template\' }"></div>',
    };
});
