package com.haizhi.hbrain.model;

import java.util.Map;

import org.springframework.data.annotation.Id;

import com.haizhi.hbrain.util.ToString;

public class NodeModel extends ToString{

	/**
	 * 
	 */
	private static final long serialVersionUID = 4948172401697253231L;
	
	@Id
	private String id;
	private String gid;
	private String rid;
	private String series;
	private String tags;
	private String price;
	private String maxPrice;
	private String minPrice;
	private String priceCurrency;
	private String unitText;
	private String priceType;
	private String productionYear;
	private String validDate;
	private String seller;
	private String productGrade;
	private String productSpecification;
	private String productPlaceOfOrigin;
	private String sellerMarket;
	private String properties;
	private String createdTime;
	private String updatedTime;
	private String format;
	private String dataSource;
	private String deletedTime;
	private Map<String, String> source;
	public String getId() {
		return id;
	}
	public void setId(String id) {
		this.id = id;
	}
	public String getGid() {
		return gid;
	}
	public void setGid(String gid) {
		this.gid = gid;
	}
	public String getRid() {
		return rid;
	}
	public void setRid(String rid) {
		this.rid = rid;
	}
	public String getSeries() {
		return series;
	}
	public void setSeries(String series) {
		this.series = series;
	}
	public String getTags() {
		return tags;
	}
	public void setTags(String tags) {
		this.tags = tags;
	}
	public String getPrice() {
		return price;
	}
	public void setPrice(String price) {
		this.price = price;
	}
	public String getMaxPrice() {
		return maxPrice;
	}
	public void setMaxPrice(String maxPrice) {
		this.maxPrice = maxPrice;
	}
	public String getMinPrice() {
		return minPrice;
	}
	public void setMinPrice(String minPrice) {
		this.minPrice = minPrice;
	}
	public String getPriceCurrency() {
		return priceCurrency;
	}
	public void setPriceCurrency(String priceCurrency) {
		this.priceCurrency = priceCurrency;
	}
	public String getUnitText() {
		return unitText;
	}
	public void setUnitText(String unitText) {
		this.unitText = unitText;
	}
	public String getPriceType() {
		return priceType;
	}
	public void setPriceType(String priceType) {
		this.priceType = priceType;
	}
	public String getProductionYear() {
		return productionYear;
	}
	public void setProductionYear(String productionYear) {
		this.productionYear = productionYear;
	}
	public String getValidDate() {
		return validDate;
	}
	public void setValidDate(String validDate) {
		this.validDate = validDate;
	}
	public String getSeller() {
		return seller;
	}
	public void setSeller(String seller) {
		this.seller = seller;
	}
	public String getProductGrade() {
		return productGrade;
	}
	public void setProductGrade(String productGrade) {
		this.productGrade = productGrade;
	}
	public String getProductSpecification() {
		return productSpecification;
	}
	public void setProductSpecification(String productSpecification) {
		this.productSpecification = productSpecification;
	}
	public String getProductPlaceOfOrigin() {
		return productPlaceOfOrigin;
	}
	public void setProductPlaceOfOrigin(String productPlaceOfOrigin) {
		this.productPlaceOfOrigin = productPlaceOfOrigin;
	}
	public String getSellerMarket() {
		return sellerMarket;
	}
	public void setSellerMarket(String sellerMarket) {
		this.sellerMarket = sellerMarket;
	}
	public String getProperties() {
		return properties;
	}
	public void setProperties(String properties) {
		this.properties = properties;
	}
	public String getCreatedTime() {
		return createdTime;
	}
	public void setCreatedTime(String createdTime) {
		this.createdTime = createdTime;
	}
	public String getUpdatedTime() {
		return updatedTime;
	}
	public void setUpdatedTime(String updatedTime) {
		this.updatedTime = updatedTime;
	}
	public String getFormat() {
		return format;
	}
	public void setFormat(String format) {
		this.format = format;
	}
	public String getDataSource() {
		return dataSource;
	}
	public void setDataSource(String dataSource) {
		this.dataSource = dataSource;
	}
	public String getDeletedTime() {
		return deletedTime;
	}
	public void setDeletedTime(String deletedTime) {
		this.deletedTime = deletedTime;
	}
	public Map<String, String> getSource() {
		return source;
	}
	public void setSource(Map<String, String> source) {
		this.source = source;
	}
	
}
