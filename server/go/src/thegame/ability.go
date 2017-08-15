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
	{0, 1, 2, 3, 4, 5, 6, 7, 8},                            // HealthRegen
	{1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000}, // MaxHealth
	{16, 20, 24, 28, 32, 36, 40, 44, 48},                   // BodyDamage
	{8, 9, 10, 11, 12, 13, 14, 15, 16},                     // BulletSpeed
	{40, 50, 60, 70, 80, 90, 100, 110, 120},                // BulletPenetration
	{12, 15, 18, 21, 24, 27, 30, 33, 36},                   // BulletDamage
	{11, 10, 9, 8, 7, 6, 5, 4, 3},                          // Reload
	{6, 7, 8, 9, 10, 11, 12, 13, 14},                       // MovementSpeed
}
