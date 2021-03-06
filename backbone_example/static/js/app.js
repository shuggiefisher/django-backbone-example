var ENTER_KEY = 13;

(function(){
    window.Tweet = Backbone.Model.extend({
        urlRoot: TWEET_API
    });

    window.Tweets = Backbone.Collection.extend({
        urlRoot: TWEET_API,
        model: Tweet,

        maybeFetch: function(options){
            // Helper function to fetch only if this collection has not been fetched before.
            if(this._fetched){
                // If this has already been fetched, call the success, if it exists
                options.success && options.success();
                return;
            }

            // when the original success function completes mark this collection as fetched
            var self = this,
                successWrapper = function(success){
                    return function(){
                        self._fetched = true;
                        success && success.apply(this, arguments);
                    };
                };
            options.success = successWrapper(options.success);
            this.fetch(options);
        },

        getOrFetch: function(id, options){
            // Helper function to use this collection as a cache for models on the server
            var model = this.get(id);

            if(model){
                options.success && options.success(model);
                return;
            }

            model = new Tweet({
                resource_uri: id
            });

            model.fetch(options);
        }


    });

    window.TweetView = Backbone.View.extend({
        tagName: 'li',
        className: 'tweet',

        events: {
            'click .permalink': 'navigate',
            'click .destroy': 'clear',
            'dblclick .message': 'edit',
            'keypress .edit': 'updateOnEnter',
            'blur .edit': 'close',
            'change select.perms': 'updatePerms'
        },

        initialize: function(){
            this.model.bind('change', this.render, this);
        },

        navigate: function(e){
            this.trigger('navigate', this.model);
            e.preventDefault();
        },

        clear: function() {
            this.model.destroy();
        },

        edit: function() {
            if (this.model.attributes['can_edit_element'] === true) {
                $(this.el).addClass('editing');
                this.$('.edit').focus();
            }
        },

        updateOnEnter: function( e ) {
			if ( e.which === ENTER_KEY ) {
				this.close();
			}
		},

        close: function() {
			var value = this.input.val().trim();

			if ( value ) {
				this.model.save({ message: value });
			} else {
				this.clear();
			}

			$(this.el).removeClass('editing');
		},

        selectedPerms: function() {
            //ignore which one triggered this, let's update them all
            var attributes = this.model.attributes;
            $(this.el).find('.perms').each(function() {
                var $this = $(this);
                var permType = $this.data('perm-type');
                attributes[permType] = [];
                attributes['group_' + permType] = [];
                _.each($this.val(), function(resource_uri) {
                    if (resource_uri.indexOf('group') == -1) {
                        attributes[permType].push({'resource_uri': resource_uri});
                    }
                    else {
                        attributes['group_' + permType].push({'resource_uri': resource_uri});
                    }
                });
            });
            this.model.attributes = attributes;
        },

        updatePerms: function(e) {
            this.selectedPerms();
            this.model.save();
        },

        renderPermSelect: function(perm, users, groups) {
            var $select = $(ich.usersAndGroupsSelect({perm: perm}));
            var perms = users.concat(groups)
            var resources = _.map(perms, function(entity) { return entity.resource_uri; });
            _.each(resources, function(resource) {
                $select.find('option[value="' + resource + '"]').attr('selected', 'selected');
            });
            return $select[0].outerHTML;
        },

        renderPerms: function() {
            var permSelects = {};
            if (this.model.attributes['can_edit_permissions'] === true) {
                _.each(['can_view', 'can_edit', 'is_admin'], function(perm){
                    permSelects[perm + '_html'] = this.renderPermSelect(perm, this.model.attributes[perm], this.model.attributes['group_' + perm]);
                }, this);
            }
            return permSelects;
        },

        render: function(){
            var selectHTML = this.renderPerms();
            var data = _.extend(this.model.toJSON(), selectHTML);
            $(this.el).html(ich.tweetTemplate(data));
            this.input = this.$('.edit');
            return this;
        }
    });


    window.DetailApp = Backbone.View.extend({
        events: {
            'click .home': 'home'
        },

        home: function(e){
            this.trigger('home');
            e.preventDefault();
        },

        render: function(){
            $(this.el).html(ich.detailApp(this.model.toJSON()));
            return this;
        }
    });

    window.InputView = Backbone.View.extend({
        events: {
            'click .tweet': 'createTweet',
            'keypress #message': 'createOnEnter'
        },

        createOnEnter: function(e){
            if((e.keyCode || e.which) == 13){
                this.createTweet();
                e.preventDefault();
            }

        },

        createTweet: function(){
            var message = this.$('#message').val();
            if(message){
                this.collection.create({
                    message: message
                });
                this.$('#message').val('');
            }
        }

    });

    window.ListView = Backbone.View.extend({
        initialize: function(){
            _.bindAll(this, 'addOne', 'addAll', 'deleteOne');

            this.collection.bind('add', this.addOne);
            this.collection.bind('reset', this.addAll, this);
            this.collection.bind('remove', this.deleteOne, this);
            this.views = [];
        },

        addAll: function(){
            this.views = [];
            this.collection.each(this.addOne);
        },

        addOne: function(tweet){
            var view = new TweetView({
                model: tweet
            });
            $(this.el).prepend(view.render().el);
            this.views.push(view);
            view.bind('all', this.rethrow, this);
        },

        deleteOne: function(tweet) {
            view = this.views.pop(_.find(this.views, function(view) {return view.model.id == tweet.id;}));
            $(view.el).remove();
        },

        rethrow: function(){
            this.trigger.apply(this, arguments);
        }

    });

    window.ListApp = Backbone.View.extend({
        el: "#app",

        rethrow: function(){
            this.trigger.apply(this, arguments);
        },

        render: function(){
            $(this.el).html(ich.listApp({}));
            var list = new ListView({
                collection: this.collection,
                el: this.$('#tweets')
            });
            list.addAll();
            list.bind('all', this.rethrow, this);
            new InputView({
                collection: this.collection,
                el: this.$('#input')
            });
        }
    });


    window.Router = Backbone.Router.extend({
        routes: {
            '': 'list',
            ':id/': 'detail'
        },

        navigate_to: function(model){
            var path = (model && model.get('id') + '/') || '';
            this.navigate(path, true);
        },

        detail: function(){},

        list: function(){}
    });

    $(function(){
        window.app = window.app || {};
        app.router = new Router();
        app.tweets = new Tweets();
        app.list = new ListApp({
            el: $("#app"),
            collection: app.tweets
        });
        app.detail = new DetailApp({
            el: $("#app")
        });
        app.router.bind('route:list', function(){
            app.tweets.maybeFetch({
                success: _.bind(app.list.render, app.list)
            });
        });
        app.router.bind('route:detail', function(id){
            app.tweets.getOrFetch(app.tweets.urlRoot + id + '/', {
                success: function(model){
                    app.detail.model = model;
                    app.detail.render();
                }
            });
        });

        app.list.bind('navigate', app.router.navigate_to, app.router);
        app.detail.bind('home', app.router.navigate_to, app.router);
        Backbone.history.start({
            pushState: true,
            silent: app.loaded
        });
    });
})();