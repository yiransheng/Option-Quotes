$(function() {
    var url = '/admin/modify';
	
    var Stock = Backbone.Model.extend({
	    save: function() {
	        var data = {
			    'symbol' : this.get('symbol'),
				'action' : '1'
			};
			$.post(url, data);
			
		},
		del: function() {		    
			var data = {
			    'symbol' : this.get('symbol'),
				'action' : '3'
			};
			$.post(url, data);
			this.trigger("destroy");
		}
	});
    var Stocks = Backbone.Collection.extend({
        model : Stock,
        // url: 'http://localhost:8086/admin/modify'
    });
    
    var StockView = Backbone.View.extend({
        
        tagName: 'p',
        
        className: 'stock',
        
        initialize: function() {
            _.bindAll(this, 'remove', 'render')
            this.model.bind('change', this.update);
            this.model.bind('destroy', this.remove);
            this.render();
        },
        events: {
            "click .close" : "clear",
        }, 
        render: function() {
            var holder, text, link, full;
            holder = stocksView.el;
            text = this.model.get("symbol");
            link = this.model.get("cboe_id");
            full = '<a href="'+link+'">'+text+'</a>';            
            $(this.el).html(full).appendTo($(holder));  
            $('<a href="#"><span class="close">remove</span></a>').appendTo($(this.el));            
        },
        // Control
        remove: function() {
            $(this.el).remove();
        },
        update: function() {
            var text, link, full;
            text = this.model.get("symbol");
            link = this.model.get("cboe_id");
            full = '<a href="'+link+'">'+text+'</a>';
            $(this.el).html(full);
            $('<a href=""><span class="close">remove</span></a>').appendTo($(this.el));   
        },
        clear: function() {
            this.model.del();
        }
        
    });
    
    var StocksView = Backbone.View.extend({        
        
        initialize: function() {
            this.collection = new Stocks;
            this.create( url );
        },
        events: {
            "keypress input" : "createOnEnter",
        }, 
        render: function() {
           
        },
        // Control
        remove: function() {
        
        },
        create: function ( url ){
            $.get(url, function( data ){                
                for (d in data){
                    var stock = new Stock({
                        "symbol" : data[d].symbol,
                    });
                    stocksView.collection.add(stock);
                    stockViews.push(new StockView({ model: stock }));   
                }
            }, "json");
        },
        createOnEnter: function(e) {
            var text = this.$('input').val();
            if (!text || e.keyCode != 13) return;
            var stock = new Stock({
                "symbol" : text
            });
            this.collection.add(stock);
			stock.save();
            stockViews.push(new StockView({ model: stock }));
            this.$('input').val('');            
        },        
        
    });
    
    var stocksView = new StocksView({ el: '#container'});
    var stockViews = [];
    
});