package main

const (
	HealthRegen = iota
	MaxHealth
	BodyDamage
	BulletSpeed
	BulletPenetration
	BulletDamage
	Reload
	MovementSpeed
	NAbilities
)

var AbilityValues = [NAbilities][9]int{
	{1, 2, 3, 4, 5, 6, 7, 8, 9},
	{1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000},
	{8, 10, 12, 14, 16, 18, 20, 22, 24},
	{8, 10, 12, 14, 16, 18, 20, 22, 24},
	{100, 150, 200, 250, 300, 350, 400, 450, 500},
	{4, 5, 6, 7, 8, 9, 10, 11, 12},
	{11, 10, 9, 8, 7, 6, 5, 4, 3},
	{7, 8, 9, 10, 11, 12, 13, 14, 15},
}
