var ENTER_KEY = 13;

(function(){

    window.TastypieModel = Backbone.Model.extend({
        base_url: function() {
          var temp_url = Backbone.Model.prototype.url.call(this);
          return (temp_url.charAt(temp_url.length - 1) == '/' ? temp_url : temp_url+'/');
        },

        url: function() {
          return this.base_url();
        }
    });

    window.TastypieCollection = Backbone.Collection.extend({
        parse: function(response) {
            this.recent_meta = response.meta || {};
            return response.objects || response;
        }
    });

    window.Me = TastypieModel.extend({
        url: ME_RESOURCE,

        initialize: function() {
            this.bind('change', function() {
                app.connect.render(this);
            });
        }
    });

    window.Mes = TastypieCollection.extend({
        // how should I deal with a singleton collection?

        url: ME_RESOURCE,
        model: Me,

        // set this model to read only - no point, js cannot be trusted anyway

        initialize: function() {
            this.storage = new Offline.Storage('me', this, {autoPush: false});
        }

    });

    window.ConnectView = Backbone.View.extend({
        el: "#connect",

        render: function(me) {
            $(this.el).html(JST.connect(me.toJSON()));
            return this;
        }
    });

    window.Tweet = TastypieModel.extend({
        url: TWEET_RESOURCE
    });

    window.Tweets = TastypieCollection.extend({
        url: TWEET_RESOURCE,
        model: Tweet,

        initialize: function() {
            this.storage = new Offline.Storage('interlists', this, {autoPush: true});
        }

    });

    window.TweetView = Backbone.View.extend({
        tagName: 'li',
        className: 'tweet',

        events: {
            'click .permalink': 'navigate',
            'taphold .message': 'clear',
            'dblclick .message': 'edit',
            'keypress .edit': 'updateOnEnter',
            'blur .edit': 'close'
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

        render: function(){
            $(this.el).html(JST.tweetTemplateMobile(this.model.toJSON()));
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
            $(this.el).html(JST.detailApp(this.model.toJSON()));
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

            this.collection.bind('add', this.addJustOne, this);
            this.collection.bind('reset', this.addAll, this);
            this.collection.bind('remove', this.deleteOne, this);
            this.views = [];
        },

        addAll: function(){
            this.views = [];
            this.collection.each(this.addOne);
        },

        addJustOne: function(tweet) {
            this.addOne(tweet);
            this.$el.listview('refresh'); // get jqm to refresh styling to the list
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
            $(this.el).html(JST.listApp({}));
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
            app.list.$el.trigger('create'); // once all are added tell jquery mobile to style the whole page
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
        app.mes = new Mes();
        app.connect = new ConnectView({
            collection: app.mes
        });
        app.list = new ListApp({
            el: $("#app"),
            collection: app.tweets
        });
        app.detail = new DetailApp({
            el: $("#app")
        });
        app.router.bind('route:list', function(){
            // load me resource from local storage
            app.mes.fetch({
                local: true
            });

            app.tweets.fetch({
                local: true,
                success: function(tweets) {
                    app.list.render(tweets);
                }
            });

            // update me resource from server
            app.mes.storage.sync.full();
            // try and update elements in localstorage
            app.tweets.storage.sync.incremental();

        });

        app.list.bind('navigate', app.router.navigate_to, app.router);
        app.detail.bind('home', app.router.navigate_to, app.router);
        Backbone.history.start({
            pushState: true,
            silent: app.loaded
        });

        document.addEventListener("deviceready", onDeviceReady, false);
        function onDeviceReady() {
            document.addEventListener("online", reconnected, false);
        }
        function reconnected() {
            app.mes.storage.sync.full();
            app.tweets.storage.sync.incremental();
        }

        // Check if a new cache is available on page load.
        window.addEventListener('load', function(e) {

            window.applicationCache.addEventListener('updateready', function(e) {
                if (window.applicationCache.status == window.applicationCache.UPDATEREADY) {
                    // Browser downloaded a new app cache.
                    // Swap it in and reload the page to get the new hotness.
                    window.applicationCache.swapCache();
                    window.location.reload();  // don't ask if they want to reload - any changes should be in localstorage and will be synced on next page load
                } else {
                  // Manifest didn't changed. Nothing new to server.
                }
            }, false);

        }, false);
    });
})();